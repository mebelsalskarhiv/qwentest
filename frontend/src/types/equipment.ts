/**
 * Equipment and OEE TypeScript types
 */

export type EquipmentStatus = 
  | 'offline'
  | 'idle'
  | 'running'
  | 'setup'
  | 'paused'
  | 'down'
  | 'maintenance';

export type MaintenanceType = 
  | 'preventive'
  | 'corrective'
  | 'emergency'
  | 'predictive'
  | 'inspection';

export interface Equipment {
  id: number;
  tenant_id: number;
  name: string;
  code: string;
  description?: string;
  category?: string;
  type?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  location?: string;
  station_id?: number;
  status: EquipmentStatus;
  is_active: boolean;
  specifications?: Record<string, any>;
  max_speed?: number;
  rated_power?: number;
  availability_target: number;
  performance_target: number;
  quality_target: number;
  shift_duration_hours: number;
  last_maintenance_date?: string;
  next_maintenance_date?: string;
  maintenance_interval_hours?: number;
  total_operating_hours: number;
  created_at: string;
  updated_at?: string;
}

export interface OEELog {
  id: number;
  tenant_id: number;
  equipment_id: number;
  start_time: string;
  end_time: string;
  shift_number?: number;
  shift_name?: string;
  planned_production_time: number;
  operating_time: number;
  downtime_minutes: number;
  downtime_reasons?: Array<{ reason: string; duration: number }>;
  ideal_cycle_time: number;
  total_count: number;
  good_count: number;
  rejected_count: number;
  run_rate?: number;
  availability: number;
  performance: number;
  quality: number;
  oee_score: number;
  is_calculated: boolean;
  calculated_at?: string;
  equipment?: Equipment;
}

export interface MaintenanceRequest {
  id: number;
  tenant_id: number;
  equipment_id: number;
  created_by?: number;
  assigned_to?: number;
  request_number: string;
  title: string;
  description?: string;
  maintenance_type: MaintenanceType;
  priority: number;
  status: 'open' | 'in_progress' | 'waiting_parts' | 'completed' | 'cancelled';
  opened_at: string;
  started_at?: string;
  completed_at?: string;
  work_performed?: string;
  parts_used?: Array<{ part_id: number; quantity: number }>;
  labor_hours: number;
  downtime_minutes: number;
  failure_mode?: string;
  root_cause?: string;
  corrective_actions?: string;
  labor_cost: number;
  parts_cost: number;
  total_cost: number;
  attachments?: string[];
  equipment?: Equipment;
}

export interface SensorData {
  id: number;
  tenant_id: number;
  equipment_id: number;
  sensor_name: string;
  sensor_type?: string;
  unit_of_measure?: string;
  value: number;
  quality: 'GOOD' | 'BAD' | 'UNCERTAIN';
  context?: Record<string, any>;
  recorded_at: string;
  equipment?: Equipment;
}

export interface DowntimeEvent {
  id: number;
  tenant_id: number;
  equipment_id: number;
  oee_log_id?: number;
  reported_by?: number;
  start_time: string;
  end_time?: string;
  duration_minutes?: number;
  category: string;
  reason_code: string;
  reason_description?: string;
  impact_level: 'Minor' | 'Major' | 'Critical';
  affects_oee: boolean;
  resolution_notes?: string;
  resolved_by?: number;
}

export interface OEEStats {
  availability: number;
  performance: number;
  quality: number;
  oee: number;
  period: string;
  equipment_code: string;
}
