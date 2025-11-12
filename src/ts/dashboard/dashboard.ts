// Dashboard functionality
import { ApiClient } from '../api/api-client';
import { Account, Transaction, DashboardData } from '../models/types';
import Chart from 'chart.js/auto';

export async function setupDashboard(): Promise<void> {
  try {
    const apiClient = new ApiClient();
    const accounts = await apiClient.getAccounts();
    
    // If we have accounts, fetch recent transactions for the first account
    let recentTransactions: Transaction[] = [];
    if (accounts.length > 0) {
      recentTransactions = await apiClient.getTransactions(accounts[0].id);
    }
    
    // Calculate total balance
    const totalBalance = accounts.reduce((sum, account) => sum + account.balance, 0);
    
    // Create dashboard data object
    const dashboardData: DashboardData = {
      accounts,
      recentTransactions,
      totalBalance
    };
    
    // Render dashboard components
    renderAccountsList(dashboardData.accounts);
    renderRecentTransactions(dashboardData.recentTransactions);
    renderBalanceSummary(dashboardData.totalBalance);
    
    // Setup account selection change event
    setupAccountSelectionEvents(dashboardData.accounts);
    
    // Initialize charts if they exist on the page
    initializeCharts(dashboardData);
    
    console.log('Dashboard initialized successfully');
  } catch (error) {
    console.error('Failed to initialize dashboard:', error);
    showErrorMessage('Failed to load dashboard data. Please try again later.');
  }
}

function renderAccountsList(accounts: Account[]): void {
  const accountsContainer = document.getElementById('accounts-list');
  if (!accountsContainer) return;
  
  if (accounts.length === 0) {
    accountsContainer.innerHTML = `
      <div class="card bg-gray-50">
        <p class="text-gray-500">You don't have any accounts yet.</p>
        <button id="create-account-btn" class="btn-primary mt-4">Create Account</button>
      </div>
    `;
    
    // Add event listener for the create account button
    const createAccountBtn = document.getElementById('create-account-btn');
    if (createAccountBtn) {
      createAccountBtn.addEventListener('click', () => {
        // Show create account modal or redirect to create account page
        const createAccountModal = document.getElementById('create-account-modal');
        if (createAccountModal) {
          createAccountModal.classList.remove('hidden');
        }
      });
    }
    
    return;
  }
  
  // Create HTML for accounts
  const accountsHtml = accounts.map(account => `
    <div class="card mb-4" data-account-id="${account.id}">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="font-medium text-lg">${account.name}</h3>
          <p class="text-gray-500 text-sm">${account.type}</p>
        </div>
        <div class="text-right">
          <p class="font-semibold text-2xl">${formatCurrency(account.balance, account.currency)}</p>
        </div>
      </div>
      <div class="mt-4 flex space-x-2">
        <button class="btn-primary deposit-btn" data-account-id="${account.id}">Deposit</button>
        <button class="btn-secondary withdraw-btn" data-account-id="${account.id}">Withdraw</button>
        <button class="btn-secondary transfer-btn" data-account-id="${account.id}">Transfer</button>
      </div>
    </div>
  `).join('');
  
  // Add accounts to container
  accountsContainer.innerHTML = accountsHtml;
  
  // Add event listeners for account action buttons
  setupAccountActionButtons();
}

function renderRecentTransactions(transactions: Transaction[]): void {
  const transactionsContainer = document.getElementById('recent-transactions');
  if (!transactionsContainer) return;
  
  if (transactions.length === 0) {
    transactionsContainer.innerHTML = `
      <div class="card bg-gray-50">
        <p class="text-gray-500">No recent transactions.</p>
      </div>
    `;
    return;
  }
  
  // Create HTML for transactions
  const transactionsHtml = transactions.map(transaction => `
    <div class="card mb-3 ${getTransactionColorClass(transaction)}">
      <div class="flex justify-between items-center">
        <div>
          <p class="font-medium">${transaction.description || getDefaultTransactionDescription(transaction)}</p>
          <p class="text-sm text-gray-500">${formatDate(transaction.createdAt)}</p>
        </div>
        <div class="text-right">
          <p class="font-semibold ${getAmountColorClass(transaction)}">${formatAmount(transaction)}</p>
          <p class="text-xs ${getStatusColorClass(transaction.status)}">${transaction.status}</p>
        </div>
      </div>
    </div>
  `).join('');
  
  // Add transactions to container
  transactionsContainer.innerHTML = transactionsHtml;
}

function renderBalanceSummary(totalBalance: number): void {
  const balanceSummary = document.getElementById('balance-summary');
  if (!balanceSummary) return;
  
  balanceSummary.innerHTML = `
    <div class="card bg-bank-primary text-white">
      <h2 class="text-xl font-medium mb-2">Total Balance</h2>
      <p class="text-3xl font-bold">${formatCurrency(totalBalance)}</p>
    </div>
  `;
}

function setupAccountSelectionEvents(_accounts: Account[]): void {
  // Add click event to account cards to show details
  const accountCards = document.querySelectorAll('[data-account-id]');
  accountCards.forEach(card => {
    card.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      // Ignore clicks on buttons
      if (target.tagName === 'BUTTON') return;
      
      const accountId = card.getAttribute('data-account-id');
      if (accountId) {
        window.location.href = `/accounts/${accountId}`;
      }
    });
  });
}

function setupAccountActionButtons(): void {
  // Deposit buttons
  const depositButtons = document.querySelectorAll('.deposit-btn');
  depositButtons.forEach(button => {
    button.addEventListener('click', (_event) => {
      const accountId = (button as HTMLElement).getAttribute('data-account-id');
      showTransactionModal('deposit', accountId);
    });
  });
  
  // Withdraw buttons
  const withdrawButtons = document.querySelectorAll('.withdraw-btn');
  withdrawButtons.forEach(button => {
    button.addEventListener('click', (_event) => {
      const accountId = (button as HTMLElement).getAttribute('data-account-id');
      showTransactionModal('withdraw', accountId);
    });
  });
  
  // Transfer buttons
  const transferButtons = document.querySelectorAll('.transfer-btn');
  transferButtons.forEach(button => {
    button.addEventListener('click', (_event) => {
      const accountId = (button as HTMLElement).getAttribute('data-account-id');
      showTransactionModal('transfer', accountId);
    });
  });
}

function showTransactionModal(type: 'deposit' | 'withdraw' | 'transfer', accountId: string | null): void {
  // Get modal element
  const modal = document.getElementById(`${type}-modal`);
  if (!modal) return;
  
  // Set account ID in hidden field
  const accountIdField = modal.querySelector('[name="account_id"]') as HTMLInputElement;
  if (accountIdField && accountId) {
    accountIdField.value = accountId;
  }
  
  // Show the modal
  modal.classList.remove('hidden');
}

function initializeCharts(dashboardData: DashboardData): void {
  // Account balance chart
  const balanceChartCanvas = document.getElementById('balance-chart') as HTMLCanvasElement;
  if (balanceChartCanvas) {
    const ctx = balanceChartCanvas.getContext('2d');
    if (ctx) {
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: dashboardData.accounts.map(account => account.name),
          datasets: [{
            data: dashboardData.accounts.map(account => account.balance),
            backgroundColor: [
              'rgba(66, 153, 225, 0.8)',
              'rgba(72, 187, 120, 0.8)',
              'rgba(237, 100, 166, 0.8)',
              'rgba(246, 173, 85, 0.8)'
            ],
            borderColor: '#ffffff',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      });
    }
  }
  
  // Transaction history chart (last 7 days)
  const transactionChartCanvas = document.getElementById('transaction-chart') as HTMLCanvasElement;
  if (transactionChartCanvas) {
    const ctx = transactionChartCanvas.getContext('2d');
    if (ctx) {
      // Process data to get last 7 days of transactions
      const dates = getLast7Days();
      const dailyData = getDailyTransactionData(dashboardData.recentTransactions, dates);
      
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: dates.map(date => formatShortDate(date)),
          datasets: [
            {
              label: 'Deposits',
              data: dailyData.deposits,
              borderColor: 'rgba(72, 187, 120, 1)',
              backgroundColor: 'rgba(72, 187, 120, 0.1)',
              tension: 0.3,
              fill: true
            },
            {
              label: 'Withdrawals',
              data: dailyData.withdrawals.map(val => -val),  // Negate for chart
              borderColor: 'rgba(237, 100, 166, 1)',
              backgroundColor: 'rgba(237, 100, 166, 0.1)',
              tension: 0.3,
              fill: true
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              title: {
                display: true,
                text: 'Amount'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            }
          },
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      });
    }
  }
}

// Helper functions
function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency 
  }).format(amount);
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

function formatShortDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', { 
    month: 'short', 
    day: 'numeric'
  }).format(date);
}

function formatAmount(transaction: Transaction): string {
  const formatted = formatCurrency(transaction.amount);
  
  if (transaction.type === 'deposit' || 
      (transaction.type === 'transfer' && transaction.toAccountId)) {
    return `+${formatted}`;
  } else {
    return `-${formatted}`;
  }
}

function getAmountColorClass(transaction: Transaction): string {
  if (transaction.type === 'deposit' || 
      (transaction.type === 'transfer' && transaction.toAccountId)) {
    return 'text-green-600';
  } else {
    return 'text-red-600';
  }
}

function getStatusColorClass(status: string): string {
  switch (status) {
  case 'completed':
    return 'text-green-600';
  case 'pending':
    return 'text-yellow-600';
  case 'failed':
    return 'text-red-600';
  default:
    return 'text-gray-600';
  }
}

function getTransactionColorClass(transaction: Transaction): string {
  if (transaction.status === 'failed') {
    return 'bg-red-50';
  } else if (transaction.status === 'pending') {
    return 'bg-yellow-50';
  }
  return '';
}

function getDefaultTransactionDescription(transaction: Transaction): string {
  switch (transaction.type) {
  case 'deposit':
    return 'Deposit';
  case 'withdrawal':
    return 'Withdrawal';
  case 'transfer':
    return 'Transfer';
  case 'payment':
    return 'Payment';
  case 'fee':
    return 'Fee';
  case 'interest':
    return 'Interest';
  default:
    return 'Transaction';
  }
}

function getLast7Days(): Date[] {
  const dates = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    dates.push(date);
  }
  return dates;
}

function getDailyTransactionData(transactions: Transaction[], dates: Date[]): { deposits: number[], withdrawals: number[] } {
  const deposits = new Array(7).fill(0);
  const withdrawals = new Array(7).fill(0);
  
  transactions.forEach(transaction => {
    const transactionDate = new Date(transaction.createdAt);
    
    for (let i = 0; i < dates.length; i++) {
      if (isSameDay(transactionDate, dates[i])) {
        if (transaction.type === 'deposit') {
          deposits[i] += transaction.amount;
        } else if (transaction.type === 'withdrawal') {
          withdrawals[i] += transaction.amount;
        } else if (transaction.type === 'transfer') {
          if (transaction.fromAccountId) {
            withdrawals[i] += transaction.amount;
          }
          if (transaction.toAccountId) {
            deposits[i] += transaction.amount;
          }
        }
        break;
      }
    }
  });
  
  return { deposits, withdrawals };
}

function isSameDay(date1: Date, date2: Date): boolean {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate();
}

function showErrorMessage(message: string): void {
  const errorElement = document.getElementById('dashboard-error');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
  }
}