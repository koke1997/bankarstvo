// Main application entry point
import { ApiClient } from './api/api-client';
import { DashboardData, Transaction, Account } from './models/types';

/**
 * Banking application class
 */
class BankingApp {
  private apiClient: ApiClient;
  private isInitialized = false;
  
  /**
   * Initialize the application
   */
  constructor() {
    this.apiClient = new ApiClient();
    
    // Initialize the application when the DOM is loaded
    document.addEventListener('DOMContentLoaded', () => {
      this.init();
    });
  }
  
  /**
   * Initialize the application
   */
  private init(): void {
    if (this.isInitialized) return;
    
    // Check if user is logged in
    this.checkAuthState();
    
    // Initialize all event handlers
    this.initEventHandlers();
    
    // Initialize page-specific functionality
    this.initCurrentPage();
    
    this.isInitialized = true;
    console.log('Banking application initialized');
  }
  
  /**
   * Check authentication state
   */
  private checkAuthState(): void {
    // Check local storage for auth token
    const token = localStorage.getItem('auth_token');
    
    if (token) {
      this.apiClient.setAuthToken(token);
      this.loadUserProfile();
    } else {
      // If on a protected page, redirect to login
      const protectedPages = [
        '/dashboard', 
        '/accounts', 
        '/transactions',
        '/manage_accounts',
        '/transaction_history'
      ];
      
      const currentPath = window.location.pathname;
      
      if (protectedPages.some(page => currentPath.includes(page))) {
        window.location.href = '/login';
      }
    }
  }
  
  /**
   * Load user profile
   */
  private async loadUserProfile(): Promise<void> {
    try {
      const userElement = document.getElementById('current-user');
      
      if (!userElement) return;
      
      const user = await this.apiClient.getUserProfile();
      
      if (user) {
        userElement.textContent = user.username;
        userElement.classList.remove('hidden');
        
        // Show logout button
        const logoutButton = document.getElementById('logout-button');
        if (logoutButton) {
          logoutButton.classList.remove('hidden');
        }
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      // Handle expired token
      if (error instanceof Error && error.message.includes('401')) {
        this.handleLogout();
      }
    }
  }
  
  /**
   * Initialize event handlers for common elements
   */
  private initEventHandlers(): void {
    // Logout button
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
      logoutButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleLogout();
      });
    }
    
    // Form submissions
    this.initFormHandlers();
    
    // Flash messages
    this.initFlashMessages();
  }
  
  /**
   * Initialize form handlers
   */
  private initFormHandlers(): void {
    // Login form
    const loginForm = document.getElementById('login-form') as HTMLFormElement;
    if (loginForm) {
      loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleLoginForm(loginForm);
      });
    }
    
    // Registration form
    const registerForm = document.getElementById('register-form') as HTMLFormElement;
    if (registerForm) {
      registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleRegisterForm(registerForm);
      });
    }
    
    // Create account form
    const createAccountForm = document.getElementById('create-account-form') as HTMLFormElement;
    if (createAccountForm) {
      createAccountForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleCreateAccountForm(createAccountForm);
      });
    }
    
    // Deposit form
    const depositForm = document.getElementById('deposit-form') as HTMLFormElement;
    if (depositForm) {
      depositForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleDepositForm(depositForm);
      });
    }
    
    // Withdrawal form
    const withdrawalForm = document.getElementById('withdrawal-form') as HTMLFormElement;
    if (withdrawalForm) {
      withdrawalForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleWithdrawalForm(withdrawalForm);
      });
    }
    
    // Transfer form
    const transferForm = document.getElementById('transfer-form') as HTMLFormElement;
    if (transferForm) {
      transferForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleTransferForm(transferForm);
      });
    }
  }
  
  /**
   * Initialize flash messages
   */
  private initFlashMessages(): void {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
      setTimeout(() => {
        message.classList.add('opacity-0');
        setTimeout(() => {
          message.remove();
        }, 500);
      }, 5000);
    });
  }
  
  /**
   * Handle login form submission
   */
  private async handleLoginForm(form: HTMLFormElement): Promise<void> {
    const formData = new FormData(form);
    const username = formData.get('username') as string;
    const password = formData.get('password') as string;
    const rememberMe = !!formData.get('remember_me');
    
    try {
      const response = await this.apiClient.login(username, password);
      
      if (response.success && response.data) {
        // Store token
        if (rememberMe) {
          localStorage.setItem('auth_token', response.data.id); // Using ID as token for simplicity
        } else {
          sessionStorage.setItem('auth_token', response.data.id);
        }
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        this.showError(form, response.error || 'Login failed');
      }
    } catch (error) {
      this.showError(form, 'Login failed. Please try again.');
      console.error('Login error:', error);
    }
  }
  
  /**
   * Handle registration form submission
   */
  private async handleRegisterForm(form: HTMLFormElement): Promise<void> {
    const formData = new FormData(form);
    
    const registerData = {
      username: formData.get('username') as string,
      email: formData.get('email') as string,
      password: formData.get('password') as string,
      confirmPassword: formData.get('confirm_password') as string,
      firstName: formData.get('first_name') as string,
      lastName: formData.get('last_name') as string,
      acceptTerms: !!formData.get('accept_terms')
    };
    
    try {
      const response = await this.apiClient.register(registerData);
      
      if (response.success && response.data) {
        // Show success message
        this.showSuccess(form, 'Registration successful! You can now log in.');
        
        // Clear form
        form.reset();
        
        // Redirect to login page after a delay
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        this.showError(form, response.error || 'Registration failed');
      }
    } catch (error) {
      this.showError(form, 'Registration failed. Please try again.');
      console.error('Registration error:', error);
    }
  }
  
  /**
   * Handle create account form submission
   */
  private async handleCreateAccountForm(form: HTMLFormElement): Promise<void> {
    const formData = new FormData(form);
    
    const accountData = {
      name: formData.get('account_name') as string,
      type: formData.get('account_type') as any,
      initialDeposit: parseFloat(formData.get('initial_deposit') as string),
      currency: formData.get('currency') as string
    };
    
    try {
      const response = await this.apiClient.createAccount(accountData);
      
      // Show success message
      this.showSuccess(form, 'Account created successfully!');
      
      // Clear form
      form.reset();
      
      // Redirect to accounts page after a delay
      setTimeout(() => {
        window.location.href = '/accounts';
      }, 2000);
    } catch (error) {
      this.showError(form, 'Failed to create account. Please try again.');
      console.error('Create account error:', error);
    }
  }
  
  /**
   * Handle deposit form submission
   */
  private async handleDepositForm(form: HTMLFormElement): Promise<void> {
    const formData = new FormData(form);
    
    const accountId = formData.get('account_id') as string;
    const amount = parseFloat(formData.get('amount') as string);
    const description = formData.get('description') as string;
    
    try {
      const response = await this.apiClient.createDeposit(accountId, amount, description);
      
      // Show success message
      this.showSuccess(form, 'Deposit successful!');
      
      // Clear form values except account selection
      const amountInput = form.querySelector('input[name="amount"]') as HTMLInputElement;
      const descriptionInput = form.querySelector('textarea[name="description"]') as HTMLTextAreaElement;
      
      if (amountInput) amountInput.value = '';
      if (descriptionInput) descriptionInput.value = '';
      
      // Refresh account balance if displayed on page
      this.refreshAccountBalance(accountId);
    } catch (error) {
      this.showError(form, 'Deposit failed. Please try again.');
      console.error('Deposit error:', error);
    }
  }
  
  /**
   * Handle withdrawal form submission
   */
  private async handleWithdrawalForm(form: HTMLFormElement): Promise<void> {
    const formData = new FormData(form);
    
    const accountId = formData.get('account_id') as string;
    const amount = parseFloat(formData.get('amount') as string);
    const description = formData.get('description') as string;
    
    try {
      const response = await this.apiClient.createWithdrawal(accountId, amount, description);
      
      // Show success message
      this.showSuccess(form, 'Withdrawal successful!');
      
      // Clear form values except account selection
      const amountInput = form.querySelector('input[name="amount"]') as HTMLInputElement;
      const descriptionInput = form.querySelector('textarea[name="description"]') as HTMLTextAreaElement;
      
      if (amountInput) amountInput.value = '';
      if (descriptionInput) descriptionInput.value = '';
      
      // Refresh account balance if displayed on page
      this.refreshAccountBalance(accountId);
    } catch (error) {
      this.showError(form, 'Withdrawal failed. Please try again.');
      console.error('Withdrawal error:', error);
    }
  }
  
  /**
   * Handle transfer form submission
   */
  private async handleTransferForm(form: HTMLFormElement): Promise<void> {
    const formData = new FormData(form);
    
    const fromAccountId = formData.get('from_account_id') as string;
    const toAccountId = formData.get('to_account_id') as string;
    const amount = parseFloat(formData.get('amount') as string);
    const description = formData.get('description') as string;
    
    try {
      const response = await this.apiClient.createTransfer(
        fromAccountId,
        toAccountId,
        amount,
        description
      );
      
      // Show success message
      this.showSuccess(form, 'Transfer successful!');
      
      // Clear form values except account selections
      const amountInput = form.querySelector('input[name="amount"]') as HTMLInputElement;
      const descriptionInput = form.querySelector('textarea[name="description"]') as HTMLTextAreaElement;
      
      if (amountInput) amountInput.value = '';
      if (descriptionInput) descriptionInput.value = '';
      
      // Refresh account balances if displayed on page
      this.refreshAccountBalance(fromAccountId);
      this.refreshAccountBalance(toAccountId);
    } catch (error) {
      this.showError(form, 'Transfer failed. Please try again.');
      console.error('Transfer error:', error);
    }
  }
  
  /**
   * Refresh account balance display
   */
  private async refreshAccountBalance(accountId: string): Promise<void> {
    try {
      const account = await this.apiClient.getAccountDetails(accountId);
      
      // Update balance display if it exists
      const balanceElement = document.querySelector(`[data-account-id="${accountId}"] .account-balance`);
      if (balanceElement) {
        balanceElement.textContent = account.balance.toFixed(2);
      }
    } catch (error) {
      console.error('Error refreshing account balance:', error);
    }
  }
  
  /**
   * Handle logout
   */
  private async handleLogout(): Promise<void> {
    try {
      await this.apiClient.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens
      localStorage.removeItem('auth_token');
      sessionStorage.removeItem('auth_token');
      
      // Redirect to login page
      window.location.href = '/login';
    }
  }
  
  /**
   * Initialize page-specific functionality
   */
  private initCurrentPage(): void {
    const path = window.location.pathname;
    
    if (path.includes('/dashboard')) {
      this.initDashboardPage();
    } else if (path.includes('/accounts')) {
      this.initAccountsPage();
    } else if (path.includes('/transaction_history')) {
      this.initTransactionHistoryPage();
    }
  }
  
  /**
   * Initialize dashboard page
   */
  private async initDashboardPage(): Promise<void> {
    try {
      // Load accounts and recent transactions
      const accounts = await this.apiClient.getAccounts();
      
      if (accounts.length > 0) {
        // Render accounts
        this.renderAccounts(accounts);
        
        // Get transactions for the first account
        const transactions = await this.apiClient.getTransactions(accounts[0].id, 1, 5);
        
        // Render recent transactions
        this.renderRecentTransactions(transactions);
        
        // Initialize charts
        this.initDashboardCharts(accounts);
      } else {
        // Show message for no accounts
        const accountsContainer = document.getElementById('accounts-container');
        if (accountsContainer) {
          accountsContainer.innerHTML = `
            <div class="card">
              <p>You don't have any accounts yet.</p>
              <a href="/accounts/create" class="btn btn-primary mt-4">Create an Account</a>
            </div>
          `;
        }
      }
    } catch (error) {
      console.error('Error initializing dashboard:', error);
    }
  }
  
  /**
   * Initialize accounts page
   */
  private async initAccountsPage(): Promise<void> {
    try {
      // Load accounts
      const accounts = await this.apiClient.getAccounts();
      
      // Render accounts
      this.renderAccounts(accounts);
    } catch (error) {
      console.error('Error initializing accounts page:', error);
    }
  }
  
  /**
   * Initialize transaction history page
   */
  private async initTransactionHistoryPage(): Promise<void> {
    try {
      // Get account ID from URL query param
      const urlParams = new URLSearchParams(window.location.search);
      const accountId = urlParams.get('account_id');
      
      if (accountId) {
        // Get transactions for the specified account
        const transactions = await this.apiClient.getTransactions(accountId);
        
        // Render transactions
        this.renderTransactions(transactions);
      } else {
        // Get all accounts
        const accounts = await this.apiClient.getAccounts();
        
        // Create account selector
        this.createAccountSelector(accounts, async (selectedAccountId) => {
          // Get transactions for the selected account
          const transactions = await this.apiClient.getTransactions(selectedAccountId);
          
          // Render transactions
          this.renderTransactions(transactions);
        });
      }
    } catch (error) {
      console.error('Error initializing transaction history page:', error);
    }
  }
  
  /**
   * Create account selector
   */
  private createAccountSelector(accounts: Account[], onChange: (accountId: string) => void): void {
    const container = document.getElementById('account-selector-container');
    
    if (!container || accounts.length === 0) return;
    
    // Create select element
    const select = document.createElement('select');
    select.id = 'account-selector';
    select.className = 'form-select mb-4';
    
    // Add options
    accounts.forEach(account => {
      const option = document.createElement('option');
      option.value = account.id;
      option.textContent = `${account.name} (${account.balance.toFixed(2)} ${account.currency})`;
      select.appendChild(option);
    });
    
    // Add event listener
    select.addEventListener('change', () => {
      onChange(select.value);
    });
    
    // Append to container
    container.innerHTML = '<label for="account-selector">Select Account:</label>';
    container.appendChild(select);
    
    // Trigger change event for initial load
    onChange(accounts[0].id);
  }
  
  /**
   * Render accounts
   */
  private renderAccounts(accounts: Account[]): void {
    const accountsContainer = document.getElementById('accounts-container');
    
    if (!accountsContainer) return;
    
    if (accounts.length === 0) {
      accountsContainer.innerHTML = `
        <div class="card">
          <p>You don't have any accounts yet.</p>
          <a href="/accounts/create" class="btn btn-primary mt-4">Create an Account</a>
        </div>
      `;
      return;
    }
    
    // Clear container
    accountsContainer.innerHTML = '';
    
    // Create account cards
    accounts.forEach(account => {
      const accountCard = document.createElement('div');
      accountCard.className = 'card mb-4';
      accountCard.dataset.accountId = account.id;
      
      accountCard.innerHTML = `
        <div class="flex justify-between items-center mb-2">
          <h3 class="text-lg font-semibold">${account.name}</h3>
          <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
            ${account.type}
          </span>
        </div>
        <div class="text-2xl font-bold mb-2">
          <span class="account-balance">${account.balance.toFixed(2)}</span> ${account.currency}
        </div>
        <div class="text-sm text-gray-500 mb-4">
          Status: ${account.status}
        </div>
        <div class="flex space-x-2">
          <a href="/transactions/deposit?account_id=${account.id}" class="btn btn-primary">Deposit</a>
          <a href="/transactions/withdraw?account_id=${account.id}" class="btn btn-secondary">Withdraw</a>
          <a href="/transaction_history?account_id=${account.id}" class="btn btn-secondary">Transactions</a>
        </div>
      `;
      
      accountsContainer.appendChild(accountCard);
    });
  }
  
  /**
   * Render recent transactions
   */
  private renderRecentTransactions(transactions: Transaction[]): void {
    const transactionsContainer = document.getElementById('recent-transactions-container');
    
    if (!transactionsContainer) return;
    
    if (transactions.length === 0) {
      transactionsContainer.innerHTML = '<p>No recent transactions.</p>';
      return;
    }
    
    // Create transactions table
    const table = document.createElement('div');
    table.className = 'table-container';
    
    table.innerHTML = `
      <table class="table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          ${transactions.map(transaction => `
            <tr>
              <td>${new Date(transaction.createdAt).toLocaleDateString()}</td>
              <td>
                <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                  ${transaction.type}
                </span>
              </td>
              <td class="${this.getAmountClass(transaction.type)}">
                ${this.formatAmount(transaction.type, transaction.amount)}
              </td>
              <td>
                <span class="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded">
                  ${transaction.status}
                </span>
              </td>
              <td>${transaction.description || '-'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    
    transactionsContainer.innerHTML = '';
    transactionsContainer.appendChild(table);
  }
  
  /**
   * Render transactions
   */
  private renderTransactions(transactions: Transaction[]): void {
    const transactionsContainer = document.getElementById('transactions-container');
    
    if (!transactionsContainer) return;
    
    if (transactions.length === 0) {
      transactionsContainer.innerHTML = '<p>No transactions found.</p>';
      return;
    }
    
    // Create transactions table
    this.renderRecentTransactions(transactions);
  }
  
  /**
   * Initialize dashboard charts
   */
  private initDashboardCharts(accounts: Account[]): void {
    const balanceChartCanvas = document.getElementById('balance-chart') as HTMLCanvasElement;
    
    if (!balanceChartCanvas) return;
    
    // Import Chart.js dynamically
    import('chart.js/auto').then(({ default: Chart }) => {
      // Balance chart data
      const balanceData = {
        labels: accounts.map(account => account.name),
        datasets: [{
          label: 'Account Balance',
          data: accounts.map(account => account.balance),
          backgroundColor: [
            'rgba(59, 130, 246, 0.7)',
            'rgba(16, 185, 129, 0.7)',
            'rgba(245, 158, 11, 0.7)',
            'rgba(239, 68, 68, 0.7)',
            'rgba(139, 92, 246, 0.7)'
          ],
          borderWidth: 1
        }]
      };
      
      // Create balance chart
      new Chart(balanceChartCanvas, {
        type: 'pie',
        data: balanceData,
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom'
            },
            title: {
              display: true,
              text: 'Account Balances'
            }
          }
        }
      });
    }).catch(error => {
      console.error('Error loading Chart.js:', error);
    });
  }
  
  /**
   * Get CSS class for transaction amount
   */
  private getAmountClass(type: string): string {
    switch (type) {
    case 'deposit':
    case 'interest':
      return 'text-green-600';
    case 'withdrawal':
    case 'fee':
      return 'text-red-600';
    default:
      return '';
    }
  }
  
  /**
   * Format transaction amount
   */
  private formatAmount(type: string, amount: number): string {
    switch (type) {
    case 'deposit':
    case 'interest':
      return `+${amount.toFixed(2)}`;
    case 'withdrawal':
    case 'fee':
      return `-${amount.toFixed(2)}`;
    default:
      return amount.toFixed(2);
    }
  }
  
  /**
   * Show error message
   */
  private showError(form: HTMLElement, message: string): void {
    const errorContainer = form.querySelector('.error-container');
    
    if (errorContainer) {
      errorContainer.innerHTML = `
        <div class="alert alert-danger">
          ${message}
        </div>
      `;
    } else {
      const newErrorContainer = document.createElement('div');
      newErrorContainer.className = 'error-container';
      newErrorContainer.innerHTML = `
        <div class="alert alert-danger">
          ${message}
        </div>
      `;
      form.prepend(newErrorContainer);
    }
  }
  
  /**
   * Show success message
   */
  private showSuccess(form: HTMLElement, message: string): void {
    const errorContainer = form.querySelector('.error-container');
    
    if (errorContainer) {
      errorContainer.innerHTML = `
        <div class="alert alert-success">
          ${message}
        </div>
      `;
    } else {
      const newErrorContainer = document.createElement('div');
      newErrorContainer.className = 'error-container';
      newErrorContainer.innerHTML = `
        <div class="alert alert-success">
          ${message}
        </div>
      `;
      form.prepend(newErrorContainer);
    }
  }
}

// Initialize the application
const app = new BankingApp();