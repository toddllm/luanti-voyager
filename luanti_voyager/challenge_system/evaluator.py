from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic, Callable
from datetime import datetime
import json
import logging

from .challenge import Challenge
from .submission import Submission, EvaluationResult

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ScoringCriteria:
    """Defines how a submission should be scored."""
    name: str
    description: str
    weight: float = 1.0  # Relative weight of this criteria
    min_score: float = 0.0
    max_score: float = 100.0
    evaluator: Optional[str] = None  # Name of custom evaluator function
    config: Dict[str, Any] = field(default_factory=dict)


class BaseEvaluator(ABC):
    """Base class for all challenge evaluators."""
    
    def __init__(self, challenge: Challenge):
        self.challenge = challenge
        self.scoring_criteria = self._load_scoring_criteria()
    
    def _load_scoring_criteria(self) -> List[ScoringCriteria]:
        """Load scoring criteria from challenge rules."""
        criteria_configs = self.challenge.rules.get('scoring_criteria', [])
        return [ScoringCriteria(**config) for config in criteria_configs]
    
    @abstractmethod
    async def evaluate(self, submission: Submission) -> EvaluationResult:
        """Evaluate a submission and return the results.
        
        Args:
            submission: The submission to evaluate
            
        Returns:
            EvaluationResult with the evaluation details
        """
        pass
    
    def _calculate_final_score(self, metrics: Dict[str, float]) -> float:
        """Calculate the final score based on metrics and criteria weights."""
        if not self.scoring_criteria:
            return 0.0
            
        total_weight = sum(criteria.weight for criteria in self.scoring_criteria)
        if total_weight <= 0:
            return 0.0
            
        weighted_sum = 0.0
        
        for criteria in self.scoring_criteria:
            score = metrics.get(criteria.name, 0.0)
            # Normalize score to be within min/max range
            normalized = max(criteria.min_score, min(score, criteria.max_score))
            weighted_sum += (normalized * criteria.weight)
        
        return weighted_sum / total_weight


class CompositeEvaluator(BaseEvaluator):
    """Evaluator that combines multiple evaluation strategies."""
    
    def __init__(self, challenge: Challenge, evaluators: List[Type[BaseEvaluator]]):
        super().__init__(challenge)
        self.evaluators = [evaluator(challenge) for evaluator in evaluators]
    
    async def evaluate(self, submission: Submission) -> EvaluationResult:
        """Run all evaluators and combine their results."""
        metrics = {}
        feedback = []
        
        for evaluator in self.evaluators:
            try:
                result = await evaluator.evaluate(submission)
                metrics.update(result.metrics)
                if result.feedback:
                    feedback.append(result.feedback)
            except Exception as e:
                logger.error(f"Error in evaluator {evaluator.__class__.__name__}: {str(e)}")
                continue
        
        score = self._calculate_final_score(metrics)
        
        return EvaluationResult(
            score=score,
            metrics=metrics,
            feedback="\n\n".join(filter(None, feedback)),
            evaluated_at=datetime.utcnow(),
            is_final=True
        )


class RuleBasedEvaluator(BaseEvaluator):
    """Evaluator that uses predefined rules for scoring."""
    
    async def evaluate(self, submission: Submission) -> EvaluationResult:
        """Evaluate based on predefined rules."""
        metrics = {}
        feedback = []
        
        for criteria in self.scoring_criteria:
            try:
                # Try to get a custom evaluator function
                evaluator_func = getattr(self, f"evaluate_{criteria.evaluator}", None)
                if evaluator_func and callable(evaluator_func):
                    result = await self._run_evaluator(evaluator_func, submission, criteria)
                    metrics[criteria.name] = result
                else:
                    # Default to a basic metric extraction
                    metrics[criteria.name] = self._extract_metric(submission, criteria)
                    
                feedback.append(f"{criteria.name}: {metrics[criteria.name]:.2f}")
                
            except Exception as e:
                logger.error(f"Error evaluating {criteria.name}: {str(e)}")
                metrics[criteria.name] = 0.0
        
        score = self._calculate_final_score(metrics)
        
        return EvaluationResult(
            score=score,
            metrics=metrics,
            feedback="\n".join(feedback),
            evaluated_at=datetime.utcnow(),
            is_final=True
        )
    
    async def _run_evaluator(
        self, 
        evaluator_func: Callable,
        submission: Submission,
        criteria: ScoringCriteria
    ) -> float:
        """Run an evaluator function with proper error handling."""
        try:
            if hasattr(evaluator_func, "__await__"):
                return await evaluator_func(submission, criteria)
            return evaluator_func(submission, criteria)
        except Exception as e:
            logger.error(f"Error in evaluator {evaluator_func.__name__}: {str(e)}")
            return 0.0
    
    def _extract_metric(self, submission: Submission, criteria: ScoringCriteria) -> float:
        """Extract a metric value from the submission."""
        # Try to get the metric directly from submission content
        value = submission.content.get(criteria.name, 0.0)
        
        # Ensure the value is within the allowed range
        return max(criteria.min_score, min(float(value), criteria.max_score))
