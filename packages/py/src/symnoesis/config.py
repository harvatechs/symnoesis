"""Strictly typed configuration loader for Symnoesis SYMN-01.

Loads and validates spec/config/symn-01.v0.1.yaml.
Zero hardcoded numeric defaults in application code; all constants
must be derived from this configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class VariablesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    effect_scale: float = Field(gt=0.0)
    sigma_floor: float = Field(gt=0.0)
    thresholds: dict[str, float]
    noninferiority_margin_h2: float = Field(gt=0.0)
    calibrated: bool

    @field_validator("thresholds")
    @classmethod
    def validate_thresholds(cls, v: dict[str, float]) -> dict[str, float]:
        required = {"H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"}
        missing = required - set(v.keys())
        if missing:
            raise ValueError(f"Missing required variable thresholds: {missing}")
        return v


class AssignmentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    prune_mass: float = Field(gt=0.0, lt=1.0)


class LayoutConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    resolution_default: int = Field(default=16)
    n_cell_min: float = Field(default=10.0, gt=0.0)
    coverage_80pct_rule: float = Field(default=0.8, gt=0.0, le=1.0)
    coarsening_order: list[str]


class HneConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    state_weights: list[float]
    outcome_blend: float = Field(ge=0.0, le=1.0)
    outcome_scale: float = Field(gt=0.0)

    @field_validator("state_weights")
    @classmethod
    def validate_weights(cls, v: list[float]) -> list[float]:
        if len(v) != 4:
            raise ValueError("state_weights must have exactly 4 elements")
        if abs(sum(v) - 1.0) > 1e-6:
            raise ValueError(f"state_weights must sum to 1.0, got {sum(v)}")
        return v


class SneConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    integrity: float = Field(ge=0.0, le=1.0)
    reliability: float = Field(ge=0.0, le=1.0)
    operator: float = Field(ge=0.0, le=1.0)

    @field_validator("operator")
    @classmethod
    def validate_sum(cls, v: float, info: Any) -> float:
        data = info.data
        if "integrity" in data and "reliability" in data:
            total = data["integrity"] + data["reliability"] + v
            if abs(total - 1.0) > 1e-6:
                raise ValueError(f"SNE components must sum to 1.0, got {total}")
        return v


class NetEffectsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    hne: HneConfig
    sne: SneConfig


class SqWeightsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    human: float = Field(gt=0.0)
    system: float = Field(gt=0.0)

    @field_validator("system")
    @classmethod
    def validate_weights_sum(cls, v: float, info: Any) -> float:
        data = info.data
        if "human" in data:
            total = data["human"] + v
            if abs(total - 1.0) > 1e-6:
                raise ValueError(f"SQ weights must sum to 1.0, got {total}")
        return v


class StabilityConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sigma_max: float = Field(gt=0.0)


class BootstrapConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    replicates: int = Field(gt=0)
    ci: float = Field(gt=0.0, lt=1.0)


class SqConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    weights: SqWeightsConfig
    non_compensation: bool
    stability: StabilityConfig
    gate_mode: Literal["ceiling", "multiplier"]
    gate_ceilings: dict[str, float]
    bootstrap: BootstrapConfig


class ClassesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    threshold: float = Field(gt=0.0, lt=1.0)


class ZonesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    z1_min: float
    z2_min: float
    z6_max: float
    precedence: list[str]


class TemporalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    frames_days: list[int]
    consecutive_intervals: int
    mdc_placeholder: float


class CoverConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    harm_threshold: float
    purity_min: float = Field(gt=0.0, le=1.0)
    coverage_target: float = Field(gt=0.0, le=1.0)
    n_rule_min: float = Field(gt=0.0)
    max_literals: int = Field(gt=0)


class PrivacyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    k_min: int = Field(ge=1)
    dp_epsilon: float = Field(gt=0.0)


class ReliabilityConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    alpha_min: float
    alpha_ci_lower_min: float
    min_raters: int
    min_judge_families: int


class EvidenceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    min_tier_for_certification: Literal["E0", "E1", "E2", "E3"]


class SymnoesisConfig(BaseModel):
    """Normative Symnoesis configuration model matching SPEC Appendix B."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    spec_version: str
    domains: list[str]
    variables: VariablesConfig
    assignment: AssignmentConfig
    layout: LayoutConfig
    net_effects: NetEffectsConfig
    sq: SqConfig
    classes: ClassesConfig
    zones: ZonesConfig
    temporal: TemporalConfig
    cover: CoverConfig
    privacy: PrivacyConfig
    reliability: ReliabilityConfig
    evidence: EvidenceConfig

    @classmethod
    def from_yaml_file(cls, path: Path | str) -> SymnoesisConfig:
        file_path = Path(path)
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    @classmethod
    def load_default(cls) -> SymnoesisConfig:
        """Loads default config from repository canonical location spec/config/symn-01.v0.1.yaml."""
        # Find repo root by traversing parents
        current = Path(__file__).resolve()
        for parent in current.parents:
            candidate = parent / "spec" / "config" / "symn-01.v0.1.yaml"
            if candidate.is_file():
                return cls.from_yaml_file(candidate)
        raise FileNotFoundError(
            "Could not locate spec/config/symn-01.v0.1.yaml in parent hierarchy"
        )
