// Type definitions for the banking application

// Account types
export interface Account {
  id: string;
  name: string;
  type: AccountType;
  balance: number;
  currency: string;
  status: AccountStatus;
  createdAt: string;
  updatedAt: string;
  userId: string;
}

export enum AccountType {
  CHECKING = 'checking',
  SAVINGS = 'savings',
  INVESTMENT = 'investment',
  CREDIT = 'credit',
  RETIREMENT = 'retirement'
}

export enum AccountStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  CLOSED = 'closed',
  FROZEN = 'frozen',
  PENDING = 'pending'
}

// Transaction types
export interface Transaction {
  id: string;
  type: TransactionType;
  amount: number;
  description?: string;
  status: TransactionStatus;
  createdAt: string;
  updatedAt: string;
  fromAccountId?: string;
  toAccountId?: string;
}

export enum TransactionType {
  DEPOSIT = 'deposit',
  WITHDRAWAL = 'withdrawal',
  TRANSFER = 'transfer',
  PAYMENT = 'payment',
  FEE = 'fee',
  INTEREST = 'interest'
}

export enum TransactionStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// User types
export interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
  status: UserStatus;
}

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  PENDING_VERIFICATION = 'pending_verification'
}

// Dashboard data
export interface DashboardData {
  accounts: Account[];
  recentTransactions: Transaction[];
  totalBalance: number;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Form types
export interface LoginForm {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName?: string;
  lastName?: string;
  acceptTerms: boolean;
}

export interface CreateAccountForm {
  name: string;
  type: AccountType;
  initialDeposit?: number;
  currency: string;
}

export interface TransactionForm {
  accountId: string;
  amount: number;
  description?: string;
}

export interface TransferForm {
  fromAccountId: string;
  toAccountId: string;
  amount: number;
  description?: string;
}

// Notification types
export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  read: boolean;
  createdAt: string;
  data?: any;
}

export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error'
}