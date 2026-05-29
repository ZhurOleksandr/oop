"""
Unit tests for OOP prediction engine.
Run: pytest backend/tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import MagicMock
from predictor import (
    PatientData, PredictionResult, RuleEvaluator,
    RuleBasedPredictor, PredictionEngine, RecommendationBuilder, run_algorithms
)
from database import PredictionAlgorithm, AlgorithmRule, RuleField, RuleOperator


# ── helpers ───────────────────────────────────────────────────────────────────

def _algo(disease="Тест", t_low=20, t_med=40, t_high=65, max_s=100, rules=None):
    a = MagicMock(spec=PredictionAlgorithm)
    a.id = "test-id-001"
    a.disease = disease
    a.is_active = True
    a.threshold_low = t_low
    a.threshold_medium = t_med
    a.threshold_high = t_high
    a.max_score = max_s
    a.rules = rules or []
    return a

def _rule(field, op, val=None, val2=None, val_text=None, score=10, desc="Правило"):
    r = MagicMock(spec=AlgorithmRule)
    r.id = "rule-id-001"
    r.field = field
    r.operator = op
    r.value = val
    r.value2 = val2
    r.value_text = val_text
    r.score = score
    r.description = desc
    r.sort_order = 0
    return r


# ══════════════════════════════════════════════════════════════════════════════
# PatientData — тести ООП інкапсуляції
# ══════════════════════════════════════════════════════════════════════════════

class TestPatientData:

    def test_get_field_glucose(self):
        p = PatientData(glucose=8.5)
        assert p.get_field(RuleField.glucose) == 8.5

    def test_get_field_cholesterol(self):
        p = PatientData(cholesterol=6.2)
        assert p.get_field(RuleField.cholesterol) == 6.2

    def test_get_field_systolicBP(self):
        p = PatientData(systolicBP=155)
        assert p.get_field(RuleField.systolicBP) == 155

    def test_get_field_diastolicBP(self):
        p = PatientData(diastolicBP=95)
        assert p.get_field(RuleField.diastolicBP) == 95

    def test_get_field_heartRate(self):
        p = PatientData(heart_rate=88)
        assert p.get_field(RuleField.heartRate) == 88

    def test_get_field_bmi(self):
        p = PatientData(bmi=31.4)
        assert p.get_field(RuleField.bmi) == 31.4

    def test_get_field_age(self):
        p = PatientData(age=52)
        assert p.get_field(RuleField.age) == 52

    def test_get_field_gender(self):
        p = PatientData(gender="female")
        assert p.get_field(RuleField.gender) == "female"

    def test_get_field_anamnesis(self):
        p = PatientData(anamnesis="Болить голова")
        assert p.get_field(RuleField.anamnesis) == "Болить голова"

    def test_get_field_none_default(self):
        p = PatientData()
        assert p.get_field(RuleField.glucose) is None

    def test_has_indicator_true(self):
        p = PatientData(glucose=6.0)
        assert p.has_indicator(RuleField.glucose) is True

    def test_has_indicator_false(self):
        p = PatientData()
        assert p.has_indicator(RuleField.glucose) is False

    def test_summary_includes_entered_fields(self):
        p = PatientData(glucose=7.0, age=45, systolicBP=140, diastolicBP=90)
        s = p.summary()
        assert "Глюкоза" in s
        assert "Вік" in s
        assert "АТ" in s


# ══════════════════════════════════════════════════════════════════════════════
# PredictionResult — тести dataclass
# ══════════════════════════════════════════════════════════════════════════════

class TestPredictionResult:

    def _result(self, risk="high", prob=85):
        return PredictionResult(
            disease="Тест", probability=prob, risk=risk,
            score=80, max_score=100, algorithm_id="a1"
        )

    def test_to_dict_keys(self):
        r = self._result()
        d = r.to_dict()
        assert set(d.keys()) >= {"disease", "probability", "risk", "score", "max_score", "algorithm_id", "factors"}

    def test_to_dict_values(self):
        r = self._result(prob=75, risk="medium")
        d = r.to_dict()
        assert d["probability"] == 75
        assert d["risk"] == "medium"

    def test_is_significant_high(self):
        assert self._result(risk="high").is_significant is True

    def test_is_significant_medium(self):
        assert self._result(risk="medium").is_significant is True

    def test_is_significant_low(self):
        assert self._result(risk="low").is_significant is True

    def test_is_not_significant_none(self):
        assert self._result(risk="none").is_significant is False

    def test_factors_default_empty(self):
        r = PredictionResult("D", 50, "medium", 50, 100, "a")
        assert r.factors == []


# ══════════════════════════════════════════════════════════════════════════════
# RuleEvaluator — тести кожного оператора
# ══════════════════════════════════════════════════════════════════════════════

class TestRuleEvaluator:

    def setup_method(self):
        self.ev = RuleEvaluator()

    # gt
    def test_gt_match(self):
        p = PatientData(glucose=8.0)
        r = _rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50)
        matched, factor = self.ev.evaluate(r, p)
        assert matched is True
        assert factor  # has description

    def test_gt_no_match(self):
        p = PatientData(glucose=6.5)
        r = _rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False

    def test_gt_equal_no_match(self):
        p = PatientData(glucose=7.0)
        r = _rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False  # gt is strict

    # gte
    def test_gte_equal_match(self):
        p = PatientData(glucose=7.0)
        r = _rule(RuleField.glucose, RuleOperator.gte, val=7.0, score=50)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_gte_above_match(self):
        p = PatientData(glucose=7.5)
        r = _rule(RuleField.glucose, RuleOperator.gte, val=7.0, score=50)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    # lt
    def test_lt_match(self):
        p = PatientData(temperature=35.8)
        r = _rule(RuleField.temperature, RuleOperator.lt, val=36.0, score=10)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_lt_no_match_equal(self):
        p = PatientData(temperature=36.0)
        r = _rule(RuleField.temperature, RuleOperator.lt, val=36.0, score=10)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False

    # lte
    def test_lte_equal_match(self):
        p = PatientData(heart_rate=60)
        r = _rule(RuleField.heartRate, RuleOperator.lte, val=60, score=5)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_lte_no_match(self):
        p = PatientData(heart_rate=90)
        r = _rule(RuleField.heartRate, RuleOperator.lte, val=60, score=5)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False

    # between
    def test_between_inside(self):
        p = PatientData(systolicBP=135)
        r = _rule(RuleField.systolicBP, RuleOperator.between, val=130, val2=140, score=25)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_between_lower_boundary(self):
        p = PatientData(systolicBP=130)
        r = _rule(RuleField.systolicBP, RuleOperator.between, val=130, val2=140, score=25)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_between_upper_boundary(self):
        p = PatientData(systolicBP=140)
        r = _rule(RuleField.systolicBP, RuleOperator.between, val=130, val2=140, score=25)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_between_outside_above(self):
        p = PatientData(systolicBP=145)
        r = _rule(RuleField.systolicBP, RuleOperator.between, val=130, val2=140, score=25)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False

    def test_between_outside_below(self):
        p = PatientData(systolicBP=120)
        r = _rule(RuleField.systolicBP, RuleOperator.between, val=130, val2=140, score=25)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False

    # contains
    def test_contains_match_single(self):
        p = PatientData(anamnesis="Підвищена спрага та втома")
        r = _rule(RuleField.anamnesis, RuleOperator.contains, val_text="спраг", score=20)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_contains_match_any_keyword(self):
        p = PatientData(anamnesis="Часте сечовипускання")
        r = _rule(RuleField.anamnesis, RuleOperator.contains, val_text="спраг,сечовипуск,втом", score=20)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_contains_no_match(self):
        p = PatientData(anamnesis="Головний біль")
        r = _rule(RuleField.anamnesis, RuleOperator.contains, val_text="спраг,сечовипуск", score=20)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False

    def test_contains_case_insensitive(self):
        p = PatientData(anamnesis="СПРАГА ТА ВТОМА")
        r = _rule(RuleField.anamnesis, RuleOperator.contains, val_text="спраг", score=20)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    # not_contains
    def test_not_contains_match(self):
        p = PatientData(anamnesis="Головний біль")
        r = _rule(RuleField.anamnesis, RuleOperator.not_contains, val_text="спраг", score=10)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is True

    def test_not_contains_no_match(self):
        p = PatientData(anamnesis="Підвищена спрага")
        r = _rule(RuleField.anamnesis, RuleOperator.not_contains, val_text="спраг", score=10)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False

    # None handling
    def test_none_field_returns_false(self):
        p = PatientData(glucose=None)
        r = _rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50)
        matched, _ = self.ev.evaluate(r, p)
        assert matched is False

    def test_factor_empty_when_no_match(self):
        p = PatientData(glucose=5.0)
        r = _rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50, desc="Тест")
        _, factor = self.ev.evaluate(r, p)
        assert factor == ""

    def test_factor_present_when_match(self):
        p = PatientData(glucose=9.0)
        r = _rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50, desc="Глюкоза висока")
        _, factor = self.ev.evaluate(r, p)
        assert "Глюкоза висока" in factor


# ══════════════════════════════════════════════════════════════════════════════
# RuleBasedPredictor — тести наслідування та predict()
# ══════════════════════════════════════════════════════════════════════════════

class TestRuleBasedPredictor:

    def _make_predictor(self, rules, **algo_kwargs):
        algo = _algo(rules=rules, **algo_kwargs)
        return RuleBasedPredictor(algo)

    def test_inherits_base_predictor(self):
        from predictor import BasePredictor
        pred = self._make_predictor([])
        assert isinstance(pred, BasePredictor)

    def test_get_disease_name(self):
        pred = self._make_predictor([], disease="Тестова хвороба")
        assert pred.get_disease_name() == "Тестова хвороба"

    def test_is_active_true(self):
        pred = self._make_predictor([])
        assert pred.is_active is True

    def test_is_active_false(self):
        pred = self._make_predictor([])
        pred._algorithm.is_active = False
        assert pred.is_active is False

    def test_predict_high_glucose_returns_result(self):
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=80, desc="Глюкоза > 7.0")]
        pred = self._make_predictor(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        patient = PatientData(glucose=9.0)
        result = pred.predict(patient)
        assert result is not None
        assert result.risk == "high"
        assert result.probability > 50
        assert "Глюкоза > 7.0" in result.factors

    def test_predict_normal_glucose_returns_none(self):
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=80)]
        pred = self._make_predictor(rules)
        patient = PatientData(glucose=5.0)
        result = pred.predict(patient)
        assert result is None  # нижче порогу

    def test_predict_medium_risk(self):
        rules = [_rule(RuleField.age, RuleOperator.gt, val=45, score=45)]
        pred = self._make_predictor(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        patient = PatientData(age=52)
        result = pred.predict(patient)
        assert result is not None
        assert result.risk == "medium"

    def test_predict_low_risk(self):
        rules = [_rule(RuleField.age, RuleOperator.gt, val=45, score=25)]
        pred = self._make_predictor(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        patient = PatientData(age=52)
        result = pred.predict(patient)
        assert result is not None
        assert result.risk == "low"

    def test_predict_accumulates_multiple_rules(self):
        rules = [
            _rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50, desc="Глюкоза"),
            _rule(RuleField.age, RuleOperator.gt, val=45, score=15, desc="Вік"),
        ]
        pred = self._make_predictor(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        patient = PatientData(glucose=9.0, age=52)
        result = pred.predict(patient)
        assert result is not None
        assert result.score == 65
        assert len(result.factors) == 2

    def test_predict_probability_capped_at_99(self):
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=5.0, score=200)]
        pred = self._make_predictor(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        patient = PatientData(glucose=9.0)
        result = pred.predict(patient)
        assert result.probability <= 99

    def test_rules_count(self):
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50)] * 3
        pred = self._make_predictor(rules)
        assert pred.rules_count == 3

    def test_repr(self):
        pred = self._make_predictor([], disease="Діабет")
        r = repr(pred)
        assert "RuleBasedPredictor" in r
        assert "Діабет" in r


# ══════════════════════════════════════════════════════════════════════════════
# RecommendationBuilder — тести Builder pattern
# ══════════════════════════════════════════════════════════════════════════════

class TestRecommendationBuilder:

    def test_empty_returns_normal(self):
        reco = RecommendationBuilder().build()
        assert "норми" in reco.lower() or "профілактичний" in reco.lower()

    def test_diabetes_keywords(self):
        reco = RecommendationBuilder().add_for_diseases(["Цукровий діабет 2 типу"]).build()
        assert "ендокринолог" in reco.lower()

    def test_hypertension_keywords(self):
        reco = RecommendationBuilder().add_for_diseases(["Артеріальна гіпертензія"]).build()
        assert "кардіолог" in reco.lower()

    def test_cardiac_keywords(self):
        reco = RecommendationBuilder().add_for_diseases(["Серцево-судинна недостатність"]).build()
        assert "ехокардіограф" in reco.lower() or "ехо" in reco.lower() or "екг" in reco.lower()

    def test_atherosclerosis_keywords(self):
        reco = RecommendationBuilder().add_for_diseases(["Атеросклероз"]).build()
        assert "ліпідограм" in reco.lower() or "холестерин" in reco.lower() or "статин" in reco.lower()

    def test_metabolic_keywords(self):
        reco = RecommendationBuilder().add_for_diseases(["Метаболічний синдром"]).build()
        assert "маса" in reco.lower() or "фізична" in reco.lower()

    def test_followup_added(self):
        reco = RecommendationBuilder().add_for_diseases(["Діабет"]).add_followup(3).build()
        assert "3 місяці" in reco

    def test_no_duplicates(self):
        reco = (
            RecommendationBuilder()
            .add_for_diseases(["Артеріальна гіпертензія", "Артеріальна гіпертензія"])
            .build()
        )
        # "кардіолога" should appear only once
        assert reco.count("Консультація кардіолога") == 1

    def test_method_chaining(self):
        # Builder підтримує метод chaining
        b = RecommendationBuilder()
        result = b.add_for_diseases(["Діабет"]).add_followup(3)
        assert result is b  # той самий об'єкт

    def test_multiple_diseases(self):
        reco = (
            RecommendationBuilder()
            .add_for_diseases(["Цукровий діабет 2 типу", "Артеріальна гіпертензія"])
            .build()
        )
        assert "ендокринолог" in reco.lower()
        assert "кардіолог" in reco.lower()


# ══════════════════════════════════════════════════════════════════════════════
# PredictionEngine — тести Facade pattern + поліморфізм
# ══════════════════════════════════════════════════════════════════════════════

class TestPredictionEngine:

    def _engine_with_rules(self, rules, **algo_kwargs):
        algo = _algo(rules=rules, **algo_kwargs)
        return PredictionEngine([algo])

    def test_engine_counts_predictors(self):
        algo1 = _algo(rules=[], disease="A")
        algo2 = _algo(rules=[], disease="B")
        engine = PredictionEngine([algo1, algo2])
        assert engine.predictor_count == 2

    def test_inactive_algo_skipped(self):
        algo = _algo(rules=[_rule(RuleField.glucose, RuleOperator.gt, val=5.0, score=80)])
        algo.is_active = False
        engine = PredictionEngine([algo])
        assert engine.predictor_count == 0

    def test_high_risk_appears_in_results(self):
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=80, desc="Глюкоза")]
        engine = self._engine_with_rules(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        results, _ = engine.run(PatientData(glucose=9.0))
        assert len(results) == 1
        assert results[0]["risk"] == "high"

    def test_normal_patient_no_results(self):
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=80)]
        engine = self._engine_with_rules(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        results, _ = engine.run(PatientData(glucose=5.0))
        assert results == []

    def test_results_sorted_by_probability_desc(self):
        algo_high = _algo(
            disease="Хвороба А", rules=[_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=80)],
            t_low=20, t_med=40, t_high=65, max_s=100
        )
        algo_low = _algo(
            disease="Хвороба Б", rules=[_rule(RuleField.age, RuleOperator.gt, val=40, score=25)],
            t_low=20, t_med=40, t_high=65, max_s=100
        )
        engine = PredictionEngine([algo_low, algo_high])
        results, _ = engine.run(PatientData(glucose=9.0, age=52))
        probs = [r["probability"] for r in results]
        assert probs == sorted(probs, reverse=True)

    def test_max_6_results(self):
        algos = [
            _algo(disease=f"Хвороба {i}",
                  rules=[_rule(RuleField.glucose, RuleOperator.gt, val=5.0, score=80)],
                  t_low=20, t_med=40, t_high=65, max_s=100)
            for i in range(10)
        ]
        engine = PredictionEngine(algos)
        results, _ = engine.run(PatientData(glucose=9.0))
        assert len(results) <= 6

    def test_recommendation_returned(self):
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=80, desc="Глюкоза")]
        engine = self._engine_with_rules(rules, disease="Цукровий діабет 2 типу",
                                          t_low=20, t_med=40, t_high=65, max_s=100)
        _, reco = engine.run(PatientData(glucose=9.0))
        assert isinstance(reco, str)
        assert len(reco) > 10

    def test_result_has_required_keys(self):
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=80)]
        engine = self._engine_with_rules(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        results, _ = engine.run(PatientData(glucose=9.0))
        assert len(results) == 1
        d = results[0]
        for key in ("disease", "probability", "risk", "score", "max_score", "algorithm_id", "factors"):
            assert key in d

    def test_empty_algorithms_list(self):
        engine = PredictionEngine([])
        results, reco = engine.run(PatientData(glucose=9.0))
        assert results == []
        assert "норми" in reco.lower() or "профілактичний" in reco.lower()

    def test_run_algorithms_function_wrapper(self):
        """Публічна функція run_algorithms — зворотна сумісність."""
        rules = [_rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=80)]
        algo = _algo(rules=rules, t_low=20, t_med=40, t_high=65, max_s=100)
        results, reco = run_algorithms([algo], PatientData(glucose=9.0))
        assert isinstance(results, list)
        assert isinstance(reco, str)

    def test_factors_list_in_result(self):
        rules = [
            _rule(RuleField.glucose, RuleOperator.gt, val=7.0, score=50, desc="Глюкоза > 7"),
            _rule(RuleField.age, RuleOperator.gt, val=45, score=20, desc="Вік > 45"),
        ]
        engine = self._engine_with_rules(rules, t_low=20, t_med=40, t_high=65, max_s=100)
        results, _ = engine.run(PatientData(glucose=9.0, age=50))
        assert "Глюкоза > 7" in results[0]["factors"]
        assert "Вік > 45" in results[0]["factors"]
