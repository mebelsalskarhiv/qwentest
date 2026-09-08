/**
 * Documents TypeScript types
 */

export type DocumentCategoryType = 
  | 'technical'
  | 'quality'
  | 'safety'
  | 'process'
  | 'regulatory'
  | 'other';

export type DocumentStatus = 
  | 'draft'
  | 'in_review'
  | 'approved'
  | 'obsolete'
  | 'archived';

export type DocumentFileType = 
  | 'pdf'
  | 'docx'
  | 'xlsx'
  | 'dwg'
  | 'image'
  | 'other';

export interface DocumentCategory {
  id: number;
  tenant_id: number;
  name: string;
  code: string;
  description?: string;
  parent_id?: number;
  category_type: DocumentCategoryType;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  id: number;
  tenant_id: number;
  category_id: number;
  title: string;
  code: string;
  description?: string;
  status: DocumentStatus;
  version: string;
  owner_id?: number;
  approver_id?: number;
  effective_date?: string;
  review_date?: string;
  is_mandatory: boolean;
  tags?: string[];
  linked_objects?: DocumentLink[];
  versions?: DocumentVersion[];
  current_version?: DocumentVersion;
  created_at: string;
  updated_at?: string;
  category?: DocumentCategory;
}

export interface DocumentVersion {
  id: number;
  document_id: number;
  version_number: string;
  file_name: string;
  file_path: string;
  file_type: DocumentFileType;
  file_size_bytes: number;
  change_description?: string;
  uploaded_by?: number;
  approved_by?: number;
  uploaded_at: string;
  approved_at?: string;
  is_current: boolean;
  checksum?: string;
}

export interface DocumentLink {
  id: number;
  tenant_id: number;
  document_id: number;
  link_type: 'product' | 'stage' | 'work_order' | 'production_order' | 'equipment' | 'other';
  linked_id: number;
  is_required: boolean;
  notes?: string;
  created_at: string;
}

export interface DocumentStats {
  total_documents: number;
  by_status: {
    draft: number;
    in_review: number;
    approved: number;
    obsolete: number;
    archived: number;
  };
  by_category: Array<{ name: string; count: number }>;
  mandatory_count: number;
  pending_approval: number;
  period: string;
}
