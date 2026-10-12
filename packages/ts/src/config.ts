/**
 * Normative Symnoesis configuration matching SPEC Appendix B and spec/config/symn-01.v0.1.yaml.
 */

export interface VariablesConfig {
  readonly effect_scale: number;
  readonly sigma_floor: number;
  readonly thresholds: Record<string, number>;
  readonly noninferiority_margin_h2: number;
  readonly calibrated: boolean;
}

export interface AssignmentConfig {
  readonly prune_mass: number;
}

export interface LayoutConfig {
  readonly resolution_default: number;
  readonly n_cell_min: number;
  readonly coverage_80pct_rule: number;
  readonly coarsening_order: readonly string[];
}

export interface HneConfig {
  readonly state_weights: readonly number[];
  readonly outcome_blend: number;
  readonly outcome_scale: number;
}

export interface SneConfig {
  readonly integrity: number;
  readonly reliability: number;
  readonly operator: number;
}

export interface NetEffectsConfig {
  readonly hne: HneConfig;
  readonly sne: SneConfig;
}

export interface SqWeightsConfig {
  readonly human: number;
  readonly system: number;
}

export interface StabilityConfig {
  readonly sigma_max: number;
}

export interface BootstrapConfig {
  readonly replicates: number;
  readonly ci: number;
}

export interface SqConfig {
  readonly weights: SqWeightsConfig;
  readonly non_compensation: boolean;
  readonly stability: StabilityConfig;
  readonly gate_mode: "ceiling" | "multiplier";
  readonly gate_ceilings: Record<string, number>;
  readonly bootstrap: BootstrapConfig;
}

export interface ClassesConfig {
  readonly threshold: number;
}

export interface ZonesConfig {
  readonly z1_min: number;
  readonly z2_min: number;
  readonly z6_max: number;
  readonly precedence: readonly string[];
}

export interface TemporalConfig {
  readonly frames_days: readonly number[];
  readonly consecutive_intervals: number;
  readonly mdc_placeholder: number;
}

export interface SymnConfig {
  readonly spec_version: string;
  readonly domains: readonly string[];
  readonly variables: VariablesConfig;
  readonly assignment: AssignmentConfig;
  readonly layout: LayoutConfig;
  readonly net_effects: NetEffectsConfig;
  readonly sq: SqConfig;
  readonly classes: ClassesConfig;
  readonly zones: ZonesConfig;
  readonly temporal: TemporalConfig;
}

export const DEFAULT_CONFIG: SymnConfig = {
  spec_version: "0.1.0",
  domains: ["learning", "coding", "health-information", "advice-companionship"],
  variables: {
    effect_scale: 0.5,
    sigma_floor: 0.01,
    thresholds: {
      H1: 0.5,
      H2: 0.4207,
      H3: 0.5,
      H4: 0.5,
      M1: 0.5,
      M2: 0.5,
      M3: 0.5,
      M4: 0.5,
    },
    noninferiority_margin_h2: 0.1,
    calibrated: false,
  },
  assignment: {
    prune_mass: 1.0e-4,
  },
  layout: {
    resolution_default: 16,
    n_cell_min: 10.0,
    coverage_80pct_rule: 0.8,
    coarsening_order: ["H4", "M4", "H3", "M3", "H2", "M2", "H1", "M1"],
  },
  net_effects: {
    hne: {
      state_weights: [0.25, 0.25, 0.25, 0.25],
      outcome_blend: 0.5,
      outcome_scale: 0.5,
    },
    sne: {
      integrity: 0.4,
      reliability: 0.4,
      operator: 0.2,
    },
  },
  sq: {
    weights: {
      human: 0.7,
      system: 0.3,
    },
    non_compensation: true,
    stability: {
      sigma_max: 0.5,
    },
    gate_mode: "ceiling",
    gate_ceilings: {
      "CHI-1": 0.0,
      "CHI-2": 0.0,
      "CHI-3": 0.0,
      "CHI-4": 0.25,
      "CHI-5": 0.25,
      "CHI-6": 0.25,
      "CHI-7": 0.25,
    },
    bootstrap: {
      replicates: 2000,
      ci: 0.95,
    },
  },
  classes: {
    threshold: 0.2,
  },
  zones: {
    z1_min: 60.0,
    z2_min: 25.0,
    z6_max: -25.0,
    precedence: ["Z7", "Z6", "Z5", "Z4", "Z1", "Z2", "Z3"],
  },
  temporal: {
    frames_days: [1, 7, 28, 84, 182],
    consecutive_intervals: 2,
    mdc_placeholder: 5.0,
  },
};
