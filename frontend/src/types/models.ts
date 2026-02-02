/**
 * Frontend TypeScript Types - IMMUTABLE CONTRACTS
 * Must match backend Python models exactly
 */

export enum EncryptionType {
  OPEN = "OPEN",
  WEP = "WEP",
  WPA = "WPA",
  WPA2 = "WPA2",
  WPA3 = "WPA3",
  WPA_WPA2 = "WPA/WPA2",
  WPA2_WPA3 = "WPA2/WPA3",
}

export enum CipherType {
  NONE = "NONE",
  WEP = "WEP",
  TKIP = "TKIP",
  CCMP = "CCMP",
  GCMP = "GCMP",
}

export enum AuthenticationType {
  OPEN = "OPN",
  PSK = "PSK",
  MGT = "MGT",
  SAE = "SAE",
}

export interface Client {
  mac: string;
  bssid: string;
  probes: string[];
  signal: number;
  packets: number;
  first_seen: string;
  last_seen: string;
  manufacturer?: string;
}

export interface Network {
  bssid: string;
  essid: string;
  channel: number;
  frequency: number;
  signal: number;
  encryption: EncryptionType;
  cipher: CipherType;
  authentication: AuthenticationType;
  wps: boolean;
  wps_version?: string;
  wps_locked: boolean;
  clients: Client[];
  handshake_captured: boolean;
  pmkid_captured: boolean;
  beacon_count: number;
  data_packets: number;
  first_seen: string;
  last_seen: string;
  manufacturer?: string;
}

export enum AttackType {
  DEAUTH = "deauth",
  PMKID = "pmkid",
  WPS_PIXIE = "wps_pixie",
  WPS_PIN = "wps_pin",
  HANDSHAKE_CAPTURE = "handshake_capture",
  FAKE_AP = "fake_ap",
  WEP_FRAG = "wep_frag",
  WEP_CHOP = "wep_chop",
  WEP_ARP_REPLAY = "wep_arp_replay",
}

export enum AttackStatus {
  PENDING = "pending",
  INITIALIZING = "initializing",
  RUNNING = "running",
  SUCCESS = "success",
  FAILED = "failed",
  CANCELLED = "cancelled",
  TIMEOUT = "timeout",
}

export interface AttackResult {
  success: boolean;
  message: string;
  handshake_file?: string;
  pmkid_file?: string;
  wps_pin?: string;
  wep_key?: string;
  capture_files: string[];
  packets_sent: number;
  duration_seconds: number;
}

export interface AttackConfig {
  target_bssid: string;
  target_essid: string;
  attack_type: AttackType;
  duration_seconds?: number;
  deauth_count?: number;
  channel?: number;
  interface: string;
}

export interface Attack {
  id: string;
  config: AttackConfig;
  status: AttackStatus;
  started_at: string;
  completed_at?: string;
  result?: AttackResult;
  logs: string[];
  progress_percent: number;
}

export enum CrackMode {
  WORDLIST = "wordlist",
  MASK = "mask",
  HYBRID_WORDLIST_MASK = "hybrid_wm",
  HYBRID_MASK_WORDLIST = "hybrid_mw",
  COMBINATOR = "combinator",
}

export enum JobStatus {
  QUEUED = "queued",
  PROVISIONING = "provisioning",
  STARTING = "starting",
  RUNNING = "running",
  PAUSED = "paused",
  SUCCESS = "success",
  EXHAUSTED = "exhausted",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export enum GPUProvider {
  VASTAI = "vastai",
  LAMBDA = "lambda",
  RUNPOD = "runpod",
  LOCAL = "local",
}

export interface CrackingJobConfig {
  handshake_file: string;
  bssid: string;
  essid: string;
  attack_mode: CrackMode;
  wordlist_path?: string;
  wordlist_name?: string;
  mask?: string;
  rules_file?: string;
  gpu_provider: GPUProvider;
  max_cost_usd: number;
  timeout_minutes: number;
}

export interface GPUInstance {
  instance_id: string;
  provider: GPUProvider;
  gpu_model: string;
  gpu_count: number;
  cost_per_hour: number;
  status: string;
  ip_address?: string;
}

export interface CrackingProgress {
  job_id: string;
  status: JobStatus;
  progress_percent: number;
  speed_mh_per_sec: number;
  tried_passwords: number;
  total_passwords?: number;
  eta_seconds?: number;
  current_wordlist_position?: number;
}

export interface CrackingJob {
  id: string;
  config: CrackingJobConfig;
  status: JobStatus;
  gpu_instance?: GPUInstance;
  progress: CrackingProgress;
  password?: string;
  cost_usd: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  logs: string[];
}

export enum AdapterMode {
  MANAGED = "managed",
  MONITOR = "monitor",
}

export enum AdapterStatus {
  DISCONNECTED = "disconnected",
  CONNECTED = "connected",
  INITIALIZING = "initializing",
  READY = "ready",
  ERROR = "error",
}

export interface Adapter {
  interface: string;
  driver: string;
  chipset: string;
  mac_address: string;
  mode: AdapterMode;
  status: AdapterStatus;
  current_channel?: number;
  supported_channels_2ghz: number[];
  supported_channels_5ghz: number[];
  monitor_mode_capable: boolean;
  injection_capable: boolean;
  tx_power_dbm: number;
}

export enum ScanMode {
  PASSIVE = "passive",
  ACTIVE = "active",
  BOTH = "both",
}

export enum ScanStatus {
  STOPPED = "stopped",
  STARTING = "starting",
  RUNNING = "running",
  PAUSED = "paused",
  ERROR = "error",
}

export interface ScanConfig {
  interface: string;
  mode: ScanMode;
  channels?: number[];
  hop_interval_ms: number;
  capture_file?: string;
}

export interface ScanSession {
  id: string;
  config: ScanConfig;
  status: ScanStatus;
  networks_found: number;
  clients_found: number;
  handshakes_captured: number;
  packets_captured: number;
  started_at: string;
  updated_at: string;
}

export enum ReportFormat {
  PDF = "pdf",
  HTML = "html",
  JSON = "json",
  MARKDOWN = "md",
}

export enum VulnerabilitySeverity {
  CRITICAL = "critical",
  HIGH = "high",
  MEDIUM = "medium",
  LOW = "low",
  INFO = "info",
}

export interface Finding {
  title: string;
  severity: VulnerabilitySeverity;
  description: string;
  affected_network: string;
  evidence: string[];
  remediation: string;
  cvss_score?: number;
  references: string[];
}

export interface Report {
  id: string;
  title: string;
  target_description: string;
  tester_name: string;
  organization: string;
  test_date: string;
  executive_summary: string;
  networks_tested: number;
  vulnerabilities_found: number;
  findings: Finding[];
  cracked_networks: string[];
  recommendations: string[];
  format: ReportFormat;
  file_path?: string;
  generated_at: string;
}
