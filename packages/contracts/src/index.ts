export const cleanupProvider = "google";
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
  "awaiting-approval",
  "completed",
  "failed",
] as const;

export type ScanStatus = (typeof scanStatuses)[number];

export const cleanupActionKinds = ["trash", "unsubscribe", "keep"] as const;

export type CleanupActionKind = (typeof cleanupActionKinds)[number];

export const cleanupRunStatuses = [
  "pending",
  "running",
  "completed",
  "partial-failure",
  "failed",
] as const;

export type CleanupRunStatus = (typeof cleanupRunStatuses)[number];

export const connectedAccountStatuses = [
  "connected",
  "reauthorization-required",
  "revoked",
  "disconnected",
] as const;

export type ConnectedAccountStatus = (typeof connectedAccountStatuses)[number];

export const sessionStatuses = ["anonymous", "authenticated"] as const;

export type SessionStatus = (typeof sessionStatuses)[number];

export const auditEventTypes = [
  "scan-created",
  "scan-completed",
  "scan-failed",
  "preview-generated",
  "cleanup-started",
  "cleanup-completed",
  "cleanup-failed",
  "token-reauthorization-required",
] as const;

export type AuditEventType = (typeof auditEventTypes)[number];

export const unsubscribeMethods = ["http", "mailto", "unsupported"] as const;

export type UnsubscribeMethod = (typeof unsubscribeMethods)[number];

export const executionStepStatuses = [
  "planned",
  "completed",
  "skipped",
  "failed",
] as const;

export type ExecutionStepStatus = (typeof executionStepStatuses)[number];

export interface SenderIdentity {
  name: string;
  email: string;
  domain: string;
}

export interface ConnectedAccountSummary {
  provider: typeof cleanupProvider;
  email: string;
  scopes: string[];
  status: ConnectedAccountStatus;
  connectedAt: string | null;
  lastSyncedAt: string | null;
  needsReauthorization: boolean;
}

export interface SessionUser {
  id: string;
  email: string;
  displayName: string | null;
  imageUrl: string | null;
}

export interface SessionSnapshot {
  status: SessionStatus;
  user: SessionUser | null;
  connectedAccount: ConnectedAccountSummary | null;
}

export interface ScanRequest {
  query?: string;
  batchSize?: number;
  aiClassificationEnabled: boolean;
}

export interface CleanupActionRecommendation {
  trash: boolean;
  unsubscribe: boolean;
  keep: boolean;
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
  recommendedActions: CleanupActionRecommendation;
  availableActions: CleanupActionKind[];
  confidence: number;
  reviewReasons: string[];
}

export interface SenderGroupDetail extends SenderGroupSummary {
  labels: string[];
  sampleSnippets: string[];
  unsubscribe: {
    methods: UnsubscribeMethod[];
    httpCount: number;
    mailtoCount: number;
    oneClickSupported: boolean;
  };
}

export interface ScanJobResponse {
  jobId: string;
  status: ScanStatus;
  totalIndexed: number;
  query: string;
  aiClassificationEnabled: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ScanProgressResponse extends ScanJobResponse {
  progress: {
    indexedMessages: number;
    processedBatches: number;
    nextPageToken: string | null;
  };
  groups: SenderGroupSummary[];
}

export interface ScanDetailResponse extends ScanProgressResponse {
  account: ConnectedAccountSummary | null;
  groups: SenderGroupDetail[];
}

export interface CleanupPreviewRequest {
  jobId: string;
  selectedGroupIds: string[];
}

export interface SkippedCleanupItem {
  groupId: string;
  reason: string;
}

export interface CleanupPreviewResponse {
  jobId: string;
  affectedGroups: number;
  trashCount: number;
  unsubscribeHttpCount: number;
  unsubscribeMailCount: number;
  skipped: SkippedCleanupItem[];
}

export interface CleanupExecuteRequest extends CleanupPreviewRequest {
  idempotencyKey: string;
  confirmedAt: string;
}

export interface CleanupExecuteResponse {
  runId: string;
  status: CleanupRunStatus;
  completed: number;
  failed: number;
  partialFailures: SkippedCleanupItem[];
  executedAt: string;
}

export interface CleanupExecutionStep {
  groupId: string;
  action: CleanupActionKind;
  unsubscribeMethod: UnsubscribeMethod | null;
  status: ExecutionStepStatus;
  reason: string | null;
}

export interface CleanupRunSummary {
  runId: string;
  jobId: string;
  status: CleanupRunStatus;
  completed: number;
  failed: number;
  startedAt: string;
  finishedAt: string | null;
}

export interface AuditEventSummary {
  eventId: string;
  type: AuditEventType;
  actorUserId: string;
  jobId: string | null;
  runId: string | null;
  createdAt: string;
  message: string;
}

export interface CleanupReviewState {
  selectedGroupIds: string[];
  lastPreview: CleanupPreviewResponse | null;
}

export interface ExecuteCleanupResult extends CleanupExecuteResponse {
  steps: CleanupExecutionStep[];
}

export interface RouteErrorResponse {
  error: {
    code: string;
    message: string;
  };
}

export interface GroupSelectionSummary {
  groupId: string;
  selected: boolean;
}

export interface AuditTrailResponse {
  events: AuditEventSummary[];
}

export interface CleanupPlannerSummary {
  groups: GroupSelectionSummary[];
  preview: CleanupPreviewResponse | null;
}

export interface WorkstreamDefinition {
  key: string;
  owner: string;
  scope: string;
  deliverables: string[];
}
