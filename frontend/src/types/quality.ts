/**
 * Quality Control TypeScript types
 */

export type DefectSeverity = 'minor' | 'major' | 'critical';

export type DefectStatus = 'open' | 'investigating' | 'resolved' | 'closed';

export type CorrectiveActionStatus = 'draft' | 'approved' | 'in_progress' | 'completed' | 'cancelled';

export interface DefectType {
  id: number;
  tenant_id: number;
  code: string;
  name: string;
  description?: string;
  category?: string;
  severity: DefectSeverity;
  is_active: boolean;
  created_at: string;
}

export interface QualityCheck {
  id: number;
  tenant_id: number;
  stage_id?: number;
  work_order_id?: number;
  production_order_id?: number;
  product_id?: number;
  inspected_by: number;
  check_type: 'incoming' | 'in_process' | 'final' | 'first_article' | 'random';
  status: 'pending' | 'in_progress' | 'passed' | 'failed' | 'skipped';
  planned_quantity: number;
  inspected_quantity: number;
  passed_quantity: number;
  rejected_quantity: number;
  defect_types?: DefectType[];
  defects?: QualityDefect[];
  measurements?: Record<string, number>;
  notes?: string;
  attachments?: string[];
  started_at?: string;
  completed_at?: string;
  next_check_date?: string;
}

export interface QualityDefect {
  id: number;
  tenant_id: number;
  quality_check_id: number;
  defect_type_id: number;
  quantity: number;
  severity: DefectSeverity;
  description?: string;
  location?: string;
  detected_by?: number;
  disposition: 'scrap' | 'rework' | 'use_as_is' | 'return_to_vendor';
  cost_impact?: number;
  created_at: string;
  defect_type?: DefectType;
}

export interface CorrectiveAction {
  id: number;
  tenant_id: number;
  defect_id?: number;
  quality_check_id?: number;
  request_number: string;
  title: string;
  description?: string;
  root_cause?: string;
  proposed_solution?: string;
  status: CorrectiveActionStatus;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_to?: number;
  due_date?: string;
  opened_at: string;
  approved_by?: number;
  approved_at?: string;
  started_at?: string;
  completed_at?: string;
  effectiveness_verified?: boolean;
  verification_date?: string;
  lessons_learned?: string;
  attachments?: string[];
}

export interface SPCChart {
  id: number;
  tenant_id: number;
  product_id?: number;
  stage_id?: number;
  characteristic_name: string;
  chart_type: 'xbar_r' | 'xbar_s' | 'i_mr' | 'p' | 'np' | 'c' | 'u';
  target_value: number;
  ucl?: number; // Upper Control Limit
  lcl?: number; // Lower Control Limit
  usL?: number; // Upper Specification Limit
  lsl?: number; // Lower Specification Limit
  sample_size: number;
  sampling_frequency_minutes?: number;
  is_active: boolean;
  control_limits_calculated: boolean;
  last_updated?: string;
  data_points?: SPCDataPoint[];
}

export interface SPCDataPoint {
  id: number;
  chart_id: number;
  sample_number: number;
  measurement_value: number;
  sample_values?: number[]; // For X-bar charts
  range_value?: number; // For R charts
  sigma_value?: number;
  is_out_of_control: boolean;
  violation_rules?: string[];
  recorded_at: string;
  recorded_by?: number;
}

export interface QualityStats {
  total_inspections: number;
  passed: number;
  failed: number;
  pass_rate: number;
  total_defects: number;
  defects_by_severity: {
    minor: number;
    major: number;
    critical: number;
  };
  top_defect_types: Array<{ name: string; count: number }>;
  period: string;
}
