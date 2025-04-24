import apiClient from './apiClient';

// Types
export interface Transaction {
  transaction_id: number;
  account_id: number;
  amount: number;
  type: string;
  description: string;
  date_posted: string;
  recipient_account_id?: number;
}

export interface TransactionFilter {
  startDate?: string;
  endDate?: string;
  type?: string;
  minAmount?: number;
  maxAmount?: number;
}

// Transaction service functions
export const transactionService = {
  // Get transactions for a specific account
  getAccountTransactions: async (accountId: number, filter?: TransactionFilter): Promise<Transaction[]> => {
    let url = `/accounts/${accountId}/transactions`;
    
    if (filter) {
      const params = new URLSearchParams();
      if (filter.startDate) params.append('startDate', filter.startDate);
      if (filter.endDate) params.append('endDate', filter.endDate);
      if (filter.type) params.append('type', filter.type);
      if (filter.minAmount) params.append('minAmount', filter.minAmount.toString());
      if (filter.maxAmount) params.append('maxAmount', filter.maxAmount.toString());
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
    }
    
    const response = await apiClient.get<Transaction[]>(url);
    return response.data;
  },

  // Get details of a specific transaction
  getTransactionDetails: async (transactionId: number): Promise<Transaction> => {
    const response = await apiClient.get<Transaction>(`/transactions/${transactionId}`);
    return response.data;
  },
  
  // Get a transaction receipt or PDF
  getTransactionReceipt: async (transactionId: number): Promise<Blob> => {
    const response = await apiClient.get<Blob>(`/transactions/${transactionId}/receipt`, {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default transactionService;