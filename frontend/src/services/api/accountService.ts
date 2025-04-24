import apiClient from './apiClient';

// Types
export interface Account {
  account_id: number;
  account_type: string;
  balance: number;
  currency_code: string;
  user_id: number;
  username?: string;
}

export interface CreateAccountData {
  account_type: string;
  currency_code: string;
  initial_balance?: number;
}

export interface TransferData {
  amount: number;
  recipient_account_id: number;
  description?: string;
}

// Account service functions
export const accountService = {
  // Get all accounts for the current user
  getUserAccounts: async (): Promise<Account[]> => {
    const response = await apiClient.get<Account[]>('/accounts');
    return response.data;
  },

  // Get details of a specific account
  getAccountDetails: async (accountId: number): Promise<Account> => {
    const response = await apiClient.get<Account>(`/accounts/${accountId}`);
    return response.data;
  },

  // Create a new account
  createAccount: async (accountData: CreateAccountData): Promise<Account> => {
    const response = await apiClient.post<Account>('/accounts', accountData);
    return response.data;
  },

  // Transfer money between accounts
  transferMoney: async (sourceAccountId: number, transferData: TransferData): Promise<any> => {
    const response = await apiClient.post<any>(`/accounts/${sourceAccountId}/transfer`, transferData);
    return response.data;
  },

  // Get available currencies for account creation
  getAvailableCurrencies: async (): Promise<{ code: string; name: string }[]> => {
    const response = await apiClient.get<{ code: string; name: string }[]>('/currencies');
    return response.data;
  },

  // Search for accounts by username (for transfers)
  searchAccounts: async (username: string): Promise<Account[]> => {
    const response = await apiClient.get<Account[]>(`/search/accounts?username=${encodeURIComponent(username)}`);
    return response.data;
  }
};

export default accountService;