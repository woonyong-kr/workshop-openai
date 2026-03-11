export const defaultScanQuery = "in:anywhere -in:chats";
export const defaultScanBatchSize = 100;

export const mailClassifications = [
  "newsletter",
  "spam",
  "personal-contact",
  "transactional",
  "social",
  "organization",
  "unknown",
] as const;

export type MailClassification = (typeof mailClassifications)[number];

export const senderTypes = [
  "personal-provider",
  "newsletter-platform",
  "organization-domain",
  "commerce",
  "social-platform",
  "unknown",
] as const;

export type SenderType = (typeof senderTypes)[number];

export const scanStatuses = [
  "queued",
  "running",
  "completed",
  "failed",
] as const;

export type ScanStatus = (typeof scanStatuses)[number];

export interface SenderIdentity {
  name: string;
  email: string;
  domain: string;
}

export interface SenderGroupSummary {
  groupId: string;
  classification: MailClassification;
  senderType: SenderType;
  sender: SenderIdentity;
  messageCount: number;
  latestDate: string | null;
  approximateTopics: string[];
  summary: string;
  sampleSubjects: string[];
  recommendedActions: {
    trash: boolean;
    unsubscribe: boolean;
    keep: boolean;
  };
}

export interface ScanJobResponse {
  jobId: string;
  status: ScanStatus;
  totalIndexed: number;
}

export interface ScanProgressResponse extends ScanJobResponse {
  progress: {
    indexedMessages: number;
    processedBatches: number;
    nextPageToken: string | null;
  };
  groups: SenderGroupSummary[];
}

export interface CleanupPreviewRequest {
  jobId: string;
  selectedGroupIds: string[];
}

export interface CleanupPreviewResponse {
  trashCount: number;
  unsubscribeHttpCount: number;
  unsubscribeMailCount: number;
  skipped: Array<{
    groupId: string;
    reason: string;
  }>;
}

export interface CleanupExecuteRequest extends CleanupPreviewRequest {
  idempotencyKey: string;
}

export interface CleanupExecuteResponse {
  runId: string;
  completed: number;
  failed: number;
  partialFailures: Array<{
    groupId: string;
    reason: string;
  }>;
}

export interface WorkstreamDefinition {
  key: string;
  owner: string;
  scope: string;
  deliverables: string[];
}
