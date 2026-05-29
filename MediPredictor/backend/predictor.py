"""
predictor.py — Рушій прогнозування захворювань (ООП-архітектура)
=================================================================

Ієрархія класів:
  BasePredictor          (ABC — абстрактний базовий клас)
   └── RuleBasedPredictor     (реалізація через правила з БД)

  PatientData            (dataclass — інкапсуляція даних пацієнта)
  RuleEvaluator          (клас-стратегія оцінки одного правила)
  PredictionResult       (dataclass — результат одного прогнозу)
  PredictionEngine       (фасад — координує всі прогнози)

Принципи ООП:
  • Абстракція    — BasePredictor визначає інтерфейс без реалізації
  • Інкапсуляція  — PatientData приховує логіку доступу до полів
  • Наслідування  — RuleBasedPredictor успадковує BasePredictor
  • Поліморфізм   — predict() викликається однаково для будь-якого Predictor
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from database import PredictionAlgorithm, AlgorithmRule, RuleOperator, RuleField

logger = logging.getLogger("medipredictor.predictor")


# ══════════════════════════════════════════════════════════════════════════════
# PatientData — інкапсуляція вхідних даних пацієнта
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PatientData:
    """
    Нормалізований набір клінічних показників пацієнта.

    Інкапсулює доступ до полів: зовнішній код використовує
    get_field(field_name) замість прямого звернення до атрибутів,
    що дозволяє легко додавати нові показники без змін у викликачах.
    """
    glucose:     float | None = None   # ммоль/л
    cholesterol: float | None = None   # ммоль/л
    systolicBP:  int   | None = None   # мм рт.ст.
    diastolicBP: int   | None = None   # мм рт.ст.
    heart_rate:  int   | None = None   # уд/хв
    temperature: float | None = None   # °C
    bmi:         float | None = None   # кг/м²
    age:         int         = 0
    gender:      str         = "male"
    anamnesis:   str         = ""

    # ── приватний маппінг field → атрибут ──────────────────────────────────
    _FIELD_MAP: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        # Ініціалізуємо маппінг після створення об'єкта
        self._FIELD_MAP = {
            RuleField.glucose:     lambda: self.glucose,
            RuleField.cholesterol: lambda: self.cholesterol,
            RuleField.systolicBP:  lambda: self.systolicBP,
            RuleField.diastolicBP: lambda: self.diastolicBP,
            RuleField.heartRate:   lambda: self.heart_rate,
            RuleField.temperature: lambda: self.temperature,
            RuleField.bmi:         lambda: self.bmi,
            RuleField.age:         lambda: self.age,
            RuleField.gender:      lambda: self.gender,
            RuleField.anamnesis:   lambda: self.anamnesis,
        }

    def get_field(self, field_name: str) -> Any:
        """
        Повертає значення показника за ім'ям поля.
        Використовує ледаче обчислення через lambda.
        """
        getter = self._FIELD_MAP.get(field_name)
        return getter() if getter else None

    def has_indicator(self, field_name: str) -> bool:
        """Перевіряє, чи введено показник (не None)."""
        val = self.get_field(field_name)
        return val is not None

    def summary(self) -> str:
        """Текстове зведення введених показників (для логування)."""
        parts = []
        if self.glucose:      parts.append(f"Глюкоза={self.glucose}")
        if self.cholesterol:  parts.append(f"Холестерин={self.cholesterol}")
        if self.systolicBP:   parts.append(f"АТ={self.systolicBP}/{self.diastolicBP}")
        if self.heart_rate:   parts.append(f"ЧСС={self.heart_rate}")
        if self.bmi:          parts.append(f"ІМТ={self.bmi}")
        parts.append(f"Вік={self.age}")
        return ", ".join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# PredictionResult — інкапсуляція результату одного прогнозу
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PredictionResult:
    """Результат застосування одного алгоритму до даних пацієнта."""
    disease:      str
    probability:  int        # 0–99 %
    risk:         str        # 'low' | 'medium' | 'high'
    score:        int        # набрані бали
    max_score:    int        # максимально можливі бали
    algorithm_id: str
    factors:      list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Серіалізація для збереження в JSONB PostgreSQL."""
        return {
            "disease":      self.disease,
            "probability":  self.probability,
            "risk":         self.risk,
            "score":        self.score,
            "max_score":    self.max_score,
            "algorithm_id": self.algorithm_id,
            "factors":      self.factors,
        }

    @property
    def is_significant(self) -> bool:
        """True, якщо ризик вище нижнього порогу."""
        return self.risk != "none"


# ══════════════════════════════════════════════════════════════════════════════
# RuleEvaluator — стратегія оцінки одного правила
# ══════════════════════════════════════════════════════════════════════════════

class RuleEvaluator:
    """
    Відповідає за перевірку одного правила алгоритму проти даних пацієнта.

    Інкапсулює всю логіку порівняння, захищаючи викликача
    від деталей реалізації операторів.
    """

    # Оператори що порівнюють числові значення
    _NUMERIC_OPS = {
        RuleOperator.gt:      lambda v, r: float(v) >  float(r),
        RuleOperator.gte:     lambda v, r: float(v) >= float(r),
        RuleOperator.lt:      lambda v, r: float(v) <  float(r),
        RuleOperator.lte:     lambda v, r: float(v) <= float(r),
        RuleOperator.eq:      lambda v, r: str(v).lower() == str(r).lower(),
    }

    def evaluate(self, rule: AlgorithmRule, patient: PatientData) -> tuple[bool, str]:
        """
        Оцінює одне правило.

        Returns:
            (matched: bool, factor_description: str)
        """
        val = patient.get_field(rule.field)
        if val is None:
            return False, ""

        try:
            matched = self._apply_operator(rule, val)
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            logger.warning("Rule evaluation error: %s — %s", rule.id, exc)
            return False, ""

        factor = rule.description or f"{rule.field} {rule.operator} {rule.value}"
        return matched, factor if matched else ""

    def _apply_operator(self, rule: AlgorithmRule, val: Any) -> bool:
        """Внутрішній диспетч операторів (закрита логіка)."""
        op = rule.operator

        # Числові оператори
        if op in self._NUMERIC_OPS:
            return self._NUMERIC_OPS[op](val, rule.value_text or rule.value)

        # Між значеннями
        if op == RuleOperator.between:
            return float(rule.value) <= float(val) <= float(rule.value2)

        # Текстовий пошук в анамнезі
        if op == RuleOperator.contains:
            keywords = [k.strip().lower() for k in (rule.value_text or "").split(",") if k.strip()]
            return any(k in str(val).lower() for k in keywords)

        if op == RuleOperator.not_contains:
            keywords = [k.strip().lower() for k in (rule.value_text or "").split(",") if k.strip()]
            return not any(k in str(val).lower() for k in keywords)

        return False


# ══════════════════════════════════════════════════════════════════════════════
# BasePredictor — абстрактний базовий клас (Абстракція + Поліморфізм)
# ══════════════════════════════════════════════════════════════════════════════

class BasePredictor(ABC):
    """
    Абстрактний базовий клас для всіх предикторів захворювань.

    Визначає контракт: будь-який предиктор повинен реалізувати
    методи predict() та get_disease_name().

    Це забезпечує поліморфізм: PredictionEngine може викликати
    predict() на будь-якому предикторі, не знаючи його конкретного типу.
    """

    @abstractmethod
    def predict(self, patient: PatientData) -> PredictionResult | None:
        """
        Повертає результат прогнозу або None, якщо ризик нижче порогу.
        Кожен конкретний клас реалізує власну логіку.
        """
        ...

    @abstractmethod
    def get_disease_name(self) -> str:
        """Назва захворювання, яке прогнозує цей предиктор."""
        ...

    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Чи активний даний предиктор."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} disease='{self.get_disease_name()}'>"


# ══════════════════════════════════════════════════════════════════════════════
# RuleBasedPredictor — конкретна реалізація (Наслідування)
# ══════════════════════════════════════════════════════════════════════════════

class RuleBasedPredictor(BasePredictor):
    """
    Конкретна реалізація BasePredictor на основі правил з бази даних.

    Наслідує BasePredictor і реалізує:
      - predict()          — головна логіка обчислення балів
      - get_disease_name() — назва захворювання
      - is_active          — статус активності

    Використовує RuleEvaluator для оцінки кожного правила
    (принцип єдиної відповідальності — Single Responsibility).
    """

    def __init__(self, algorithm: PredictionAlgorithm):
        """
        Args:
            algorithm: ORM-об'єкт алгоритму з завантаженими правилами.
        """
        self._algorithm = algorithm
        self._evaluator = RuleEvaluator()   # інкапсульована залежність

    # ── Реалізація абстрактних методів ──────────────────────────────────────

    def get_disease_name(self) -> str:
        return self._algorithm.disease

    @property
    def is_active(self) -> bool:
        return self._algorithm.is_active

    def predict(self, patient: PatientData) -> PredictionResult | None:
        """
        Обчислює ризик захворювання для конкретного пацієнта.

        Алгоритм:
          1. Перебирає всі правила алгоритму
          2. Для кожного правила RuleEvaluator перевіряє умову
          3. При збігу додає бали та фіксує фактор ризику
          4. Нормалізує бали у відсотки ймовірності
          5. Визначає рівень ризику за пороговими значеннями
          6. Повертає None якщо ризик нижче мінімального порогу
        """
        total_score = 0
        matched_factors: list[str] = []

        # Перебір правил у заданому порядку (sort_order)
        for rule in sorted(self._algorithm.rules, key=lambda r: r.sort_order):
            matched, factor = self._evaluator.evaluate(rule, patient)
            if matched:
                total_score += rule.score
                if factor:
                    matched_factors.append(factor)

        risk = self._compute_risk(total_score)
        if risk == "none":
            return None   # нижче мінімального порогу — не включаємо

        probability = self._normalize_probability(total_score)

        return PredictionResult(
            disease=self._algorithm.disease,
            probability=probability,
            risk=risk,
            score=total_score,
            max_score=self._algorithm.max_score,
            algorithm_id=str(self._algorithm.id),
            factors=matched_factors,
        )

    # ── Захищені допоміжні методи (інкапсуляція) ────────────────────────────

    def _compute_risk(self, score: int) -> str:
        """Визначає рівень ризику за пороговими значеннями алгоритму."""
        if score >= self._algorithm.threshold_high:
            return "high"
        if score >= self._algorithm.threshold_medium:
            return "medium"
        if score >= self._algorithm.threshold_low:
            return "low"
        return "none"

    def _normalize_probability(self, score: int) -> int:
        """Нормалізує бали у відсотки: probability = min(99, score/max*100)."""
        if self._algorithm.max_score <= 0:
            return 0
        return min(99, round((score / self._algorithm.max_score) * 100))

    @property
    def algorithm_id(self) -> str:
        return str(self._algorithm.id)

    @property
    def rules_count(self) -> int:
        return len(self._algorithm.rules)


# ══════════════════════════════════════════════════════════════════════════════
# RecommendationBuilder — будівельник рекомендацій (Builder pattern)
# ══════════════════════════════════════════════════════════════════════════════

class RecommendationBuilder:
    """
    Будує текст клінічних рекомендацій на основі виявлених захворювань.

    Застосовує патерн Builder: поступово накопичує рекомендації
    та повертає фінальний рядок.
    """

    # База знань: ключові слова захворювань → рекомендації
    _KNOWLEDGE_BASE: dict[str, list[str]] = {
        "діабет": [
            "Направити до ендокринолога.",
            "Контроль глікемії натще та постпрандіально.",
            "Дієта з обмеженням простих вуглеводів.",
            "Самоконтроль глюкози глюкометром.",
        ],
        "гіпертен": [
            "Консультація кардіолога.",
            "Добовий моніторинг артеріального тиску (ДМАТ).",
            "Дієта з обмеженням кухонної солі (до 5 г/добу).",
            "Обмеження вживання алкоголю та кофеїну.",
        ],
        "серцево": [
            "Ехокардіографія (ЕхоКГ).",
            "ЕКГ у спокої та під навантаженням.",
            "Обмеження фізичних навантажень до уточнення діагнозу.",
            "Контроль маси тіла.",
        ],
        "атеросклер": [
            "Розгорнута ліпідограма (ЛПНЩ, ЛПВЩ, тригліцериди).",
            "Дієта з обмеженням насичених жирів та трансжирів.",
            "Розглянути статинотерапію після консультації кардіолога.",
        ],
        "метаболічний": [
            "Корекція маси тіла (цільовий ІМТ < 25).",
            "Регулярна фізична активність (≥ 150 хв/тиждень).",
            "Комплексна зміна способу життя.",
        ],
    }

    def __init__(self):
        self._recs: list[str] = []

    def add_for_diseases(self, diseases: list[str]) -> "RecommendationBuilder":
        """Додає рекомендації для списку виявлених захворювань."""
        seen: set[str] = set()
        for disease in diseases:
            d_lower = disease.lower()
            for keyword, recs in self._KNOWLEDGE_BASE.items():
                if keyword in d_lower:
                    for rec in recs:
                        if rec not in seen:
                            self._recs.append(rec)
                            seen.add(rec)
        return self   # дозволяє method chaining

    def add_followup(self, months: int = 3) -> "RecommendationBuilder":
        """Додає стандартне направлення на повторний огляд."""
        self._recs.append(f"Повторний огляд через {months} місяці.")
        return self

    def build(self) -> str:
        """Повертає фінальний рядок рекомендацій."""
        if not self._recs:
            return (
                "Показники в межах норми. "
                "Рекомендовано профілактичний огляд через 12 місяців."
            )
        return " ".join(self._recs)


# ══════════════════════════════════════════════════════════════════════════════
# PredictionEngine — фасад (Facade pattern)
# ══════════════════════════════════════════════════════════════════════════════

class PredictionEngine:
    """
    Головний координатор прогнозування.

    Реалізує патерн Facade: надає простий інтерфейс
    для складної системи предикторів і будівельника рекомендацій.

    Приймає список ORM-алгоритмів, створює для кожного
    RuleBasedPredictor і запускає прогнозування.
    """

    MAX_RESULTS = 6   # максимум захворювань у відповіді

    def __init__(self, algorithms: list[PredictionAlgorithm]):
        # Поліморфізм: зберігаємо BasePredictor, а не конкретний тип
        self._predictors: list[BasePredictor] = [
            RuleBasedPredictor(algo)
            for algo in algorithms
            if algo.is_active
        ]
        logger.debug("PredictionEngine: loaded %d active predictors", len(self._predictors))

    def run(self, patient: PatientData) -> tuple[list[dict], str]:
        """
        Запускає всі предиктори та повертає (predictions, recommendation).

        Args:
            patient: нормалізовані дані пацієнта

        Returns:
            Кортеж: (список словників для JSONB, рядок рекомендацій)
        """
        logger.info("Running prediction for patient: %s", patient.summary())

        raw_results: list[PredictionResult] = []

        # Поліморфний виклик: predict() однаковий для будь-якого BasePredictor
        for predictor in self._predictors:
            result = predictor.predict(patient)
            if result and result.is_significant:
                raw_results.append(result)

        # Сортування за ймовірністю (найвища — перша)
        raw_results.sort(key=lambda r: r.probability, reverse=True)
        top_results = raw_results[:self.MAX_RESULTS]

        # Будуємо рекомендації через RecommendationBuilder
        diseases = [r.disease for r in top_results]
        recommendation = (
            RecommendationBuilder()
            .add_for_diseases(diseases)
            .add_followup(months=3 if top_results else 12)
            .build()
        )

        predictions_json = [r.to_dict() for r in top_results]
        logger.info("Prediction complete: %d results", len(predictions_json))

        return predictions_json, recommendation

    @property
    def predictor_count(self) -> int:
        """Кількість активних предикторів."""
        return len(self._predictors)


# ══════════════════════════════════════════════════════════════════════════════
# Публічний API модуля (зворотна сумісність з routers/analyses.py)
# ══════════════════════════════════════════════════════════════════════════════

def run_algorithms(
    algorithms: list[PredictionAlgorithm],
    patient: PatientData,
) -> tuple[list[dict], str]:
    """
    Зручна функція-обгортка для використання в роутері аналізів.
    Створює PredictionEngine і запускає прогнозування.
    """
    engine = PredictionEngine(algorithms)
    return engine.run(patient)
