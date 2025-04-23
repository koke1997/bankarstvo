// API client for making HTTP requests to the banking API
import { 
  Account, 
  AccountType, 
  Transaction, 
  User, 
  ApiResponse,
  PaginatedResponse,
  CreateAccountForm,
  LoginForm,
  RegisterForm
} from '../models/types';

/**
 * API Client class for interacting with the banking API
 */
export class ApiClient {
  private baseUrl: string;
  private headers: HeadersInit;
  
  /**
   * Constructor for the API client
   * @param baseUrl Optional base URL for the API, defaults to the current domain
   */
  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || '';
    this.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }
  
  /**
   * Set the authentication token for API requests
   * @param token JWT token
   */
  setAuthToken(token: string): void {
    this.headers = {
      ...this.headers,
      'Authorization': `Bearer ${token}`
    };
  }
  
  /**
   * Clear the authentication token
   */
  clearAuthToken(): void {
    const { Authorization, ...rest } = this.headers as any;
    this.headers = rest;
  }
  
  /**
   * Make a GET request to the API
   * @param endpoint API endpoint to call
   * @param params Optional query parameters
   * @returns Promise with the response data
   */
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = this.buildUrl(endpoint, params);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.headers,
        credentials: 'include'
      });
      
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError<T>(error);
    }
  }
  
  /**
   * Make a POST request to the API
   * @param endpoint API endpoint to call
   * @param data Data to send in the request body
   * @returns Promise with the response data
   */
  async post<T>(endpoint: string, data: any): Promise<T> {
    const url = this.buildUrl(endpoint);
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.headers,
        credentials: 'include',
        body: JSON.stringify(data)
      });
      
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError<T>(error);
    }
  }
  
  /**
   * Make a PUT request to the API
   * @param endpoint API endpoint to call
   * @param data Data to send in the request body
   * @returns Promise with the response data
   */
  async put<T>(endpoint: string, data: any): Promise<T> {
    const url = this.buildUrl(endpoint);
    
    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: this.headers,
        credentials: 'include',
        body: JSON.stringify(data)
      });
      
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError<T>(error);
    }
  }
  
  /**
   * Make a DELETE request to the API
   * @param endpoint API endpoint to call
   * @returns Promise with the response data
   */
  async delete<T>(endpoint: string): Promise<T> {
    const url = this.buildUrl(endpoint);
    
    try {
      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.headers,
        credentials: 'include'
      });
      
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError<T>(error);
    }
  }
  
  /**
   * Build a URL with the base URL and endpoint
   * @param endpoint API endpoint
   * @param params Optional query parameters
   * @returns Full URL
   */
  private buildUrl(endpoint: string, params?: Record<string, string>): string {
    // Remove leading slash if present
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    
    // Build the URL
    const url = new URL(`${this.baseUrl}/${cleanEndpoint}`);
    
    // Add query parameters if provided
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }
    
    return url.toString();
  }
  
  /**
   * Handle API response
   * @param response Fetch response object
   * @returns Promise with the response data
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      // Try to parse error response
      try {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error ${response.status}`);
      } catch (jsonError) {
        throw new Error(`HTTP error ${response.status}`);
      }
    }
    
    // For 204 No Content, return empty object
    if (response.status === 204) {
      return {} as T;
    }
    
    try {
      return await response.json() as T;
    } catch (error) {
      throw new Error('Invalid JSON response from server');
    }
  }
  
  /**
   * Handle API errors
   * @param error Error object
   * @returns Never - always throws
   */
  private handleError<T>(error: any): never {
    console.error('API request failed:', error);
    throw error;
  }
  
  // ==========================================
  // Convenience methods for common API endpoints
  // ==========================================
  
  // Auth endpoints
  /**
   * Log in a user
   * @param username Username
   * @param password Password
   * @returns Promise with user data
   */
  async login(username: string, password: string): Promise<ApiResponse<User>> {
    return this.post<ApiResponse<User>>('/api/auth/login', { username, password });
  }
  
  /**
   * Register a new user
   * @param formData Registration form data
   * @returns Promise with user data
   */
  async register(formData: RegisterForm): Promise<ApiResponse<User>> {
    return this.post<ApiResponse<User>>('/api/auth/register', formData);
  }
  
  /**
   * Log out the current user
   * @returns Promise with logout status
   */
  async logout(): Promise<ApiResponse<void>> {
    const response = await this.post<ApiResponse<void>>('/api/auth/logout', {});
    this.clearAuthToken();
    return response;
  }
  
  // Account endpoints
  /**
   * Get all accounts for the current user
   * @returns Promise with accounts data
   */
  async getAccounts(): Promise<Account[]> {
    const response = await this.get<ApiResponse<Account[]>>('/api/accounts');
    return response.data || [];
  }
  
  /**
   * Get account details by ID
   * @param accountId Account ID
   * @returns Promise with account data
   */
  async getAccountDetails(accountId: string): Promise<Account> {
    const response = await this.get<ApiResponse<Account>>(`/api/accounts/${accountId}`);
    return response.data as Account;
  }
  
  /**
   * Create a new account
   * @param accountData Account data
   * @returns Promise with new account data
   */
  async createAccount(accountData: CreateAccountForm): Promise<Account> {
    const response = await this.post<ApiResponse<Account>>('/api/accounts', accountData);
    return response.data as Account;
  }
  
  /**
   * Close an account
   * @param accountId Account ID
   * @returns Promise with status
   */
  async closeAccount(accountId: string): Promise<ApiResponse<void>> {
    return this.put<ApiResponse<void>>(`/api/accounts/${accountId}/close`, {});
  }
  
  // Transaction endpoints
  /**
   * Get transactions for an account
   * @param accountId Account ID
   * @param page Page number (optional)
   * @param pageSize Number of items per page (optional)
   * @returns Promise with transactions data
   */
  async getTransactions(accountId: string, page?: number, pageSize?: number): Promise<Transaction[]> {
    const params: Record<string, string> = {};
    
    if (page !== undefined) {
      params.page = page.toString();
    }
    
    if (pageSize !== undefined) {
      params.pageSize = pageSize.toString();
    }
    
    const response = await this.get<ApiResponse<Transaction[]>>(
      `/api/accounts/${accountId}/transactions`, 
      params
    );
    
    return response.data || [];
  }
  
  /**
   * Create a deposit transaction
   * @param accountId Account ID
   * @param amount Amount to deposit
   * @param description Optional description
   * @returns Promise with transaction data
   */
  async createDeposit(accountId: string, amount: number, description?: string): Promise<Transaction> {
    const response = await this.post<ApiResponse<Transaction>>('/api/transactions/deposit', {
      accountId,
      amount,
      description
    });
    
    return response.data as Transaction;
  }
  
  /**
   * Create a withdrawal transaction
   * @param accountId Account ID
   * @param amount Amount to withdraw
   * @param description Optional description
   * @returns Promise with transaction data
   */
  async createWithdrawal(accountId: string, amount: number, description?: string): Promise<Transaction> {
    const response = await this.post<ApiResponse<Transaction>>('/api/transactions/withdraw', {
      accountId,
      amount,
      description
    });
    
    return response.data as Transaction;
  }
  
  /**
   * Create a transfer transaction
   * @param fromAccountId Source account ID
   * @param toAccountId Destination account ID
   * @param amount Amount to transfer
   * @param description Optional description
   * @returns Promise with transaction data
   */
  async createTransfer(
    fromAccountId: string, 
    toAccountId: string, 
    amount: number, 
    description?: string
  ): Promise<Transaction> {
    const response = await this.post<ApiResponse<Transaction>>('/api/transactions/transfer', {
      fromAccountId,
      toAccountId,
      amount,
      description
    });
    
    return response.data as Transaction;
  }
  
  // User profile endpoints
  /**
   * Get current user profile
   * @returns Promise with user data
   */
  async getUserProfile(): Promise<User> {
    const response = await this.get<ApiResponse<User>>('/api/user/profile');
    return response.data as User;
  }
  
  /**
   * Update user profile
   * @param userData User data to update
   * @returns Promise with updated user data
   */
  async updateUserProfile(userData: Partial<User>): Promise<User> {
    const response = await this.put<ApiResponse<User>>('/api/user/profile', userData);
    return response.data as User;
  }
}