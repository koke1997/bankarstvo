// Transaction forms functionality
import { ApiClient } from '../api/api-client';
import { Account } from '../models/types';

export function setupTransactionForms(): void {
  // Initialize all transaction forms on the page
  initializeDepositForm();
  initializeWithdrawForm();
  initializeTransferForm();
  
  // Setup modal close buttons
  setupCloseModalButtons();
}

function initializeDepositForm(): void {
  const depositForm = document.getElementById('deposit-form') as HTMLFormElement;
  if (!depositForm) return;
  
  depositForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const formData = new FormData(depositForm);
    const accountId = formData.get('account_id') as string;
    const amount = parseFloat(formData.get('amount') as string);
    const description = formData.get('description') as string;
    
    if (!accountId || isNaN(amount) || amount <= 0) {
      showFormError(depositForm, 'Please enter a valid amount.');
      return;
    }
    
    try {
      const apiClient = new ApiClient();
      const transaction = await apiClient.createDeposit(accountId, amount, description);
      
      showFormSuccess(depositForm, 'Deposit successful!');
      
      // Reset form
      depositForm.reset();
      
      // Close modal
      const modal = document.getElementById('deposit-modal');
      if (modal) {
        modal.classList.add('hidden');
      }
      
      // Refresh the page after a delay to show updated balance
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      console.error('Deposit failed:', error);
      showFormError(depositForm, 'Deposit failed. Please try again.');
    }
  });
}

function initializeWithdrawForm(): void {
  const withdrawForm = document.getElementById('withdraw-form') as HTMLFormElement;
  if (!withdrawForm) return;
  
  withdrawForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const formData = new FormData(withdrawForm);
    const accountId = formData.get('account_id') as string;
    const amount = parseFloat(formData.get('amount') as string);
    const description = formData.get('description') as string;
    
    if (!accountId || isNaN(amount) || amount <= 0) {
      showFormError(withdrawForm, 'Please enter a valid amount.');
      return;
    }
    
    try {
      const apiClient = new ApiClient();
      
      // Get current balance to validate withdrawal
      const account = await apiClient.getAccountDetails(accountId);
      
      if (amount > account.balance) {
        showFormError(withdrawForm, 'Insufficient funds for withdrawal.');
        return;
      }
      
      const transaction = await apiClient.createWithdrawal(accountId, amount, description);
      
      showFormSuccess(withdrawForm, 'Withdrawal successful!');
      
      // Reset form
      withdrawForm.reset();
      
      // Close modal
      const modal = document.getElementById('withdraw-modal');
      if (modal) {
        modal.classList.add('hidden');
      }
      
      // Refresh the page after a delay to show updated balance
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      console.error('Withdrawal failed:', error);
      showFormError(withdrawForm, 'Withdrawal failed. Please try again.');
    }
  });
}

function initializeTransferForm(): void {
  const transferForm = document.getElementById('transfer-form') as HTMLFormElement;
  if (!transferForm) return;
  
  // Setup source account field
  const fromAccountId = transferForm.querySelector('[name="from_account_id"]') as HTMLSelectElement;
  
  // Dynamically set the source account if there's one selected
  // This is used when a user clicks "Transfer" on a specific account card
  const accountIdField = transferForm.querySelector('[name="account_id"]') as HTMLInputElement;
  if (accountIdField && accountIdField.value && fromAccountId) {
    fromAccountId.value = accountIdField.value;
  }
  
  // Populate destination account dropdown when form loads
  populateAccountDropdown();
  
  transferForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const formData = new FormData(transferForm);
    const fromAccountId = formData.get('from_account_id') as string;
    const toAccountId = formData.get('to_account_id') as string;
    const amount = parseFloat(formData.get('amount') as string);
    const description = formData.get('description') as string;
    
    if (!fromAccountId || !toAccountId || isNaN(amount) || amount <= 0) {
      showFormError(transferForm, 'Please fill in all required fields with valid values.');
      return;
    }
    
    if (fromAccountId === toAccountId) {
      showFormError(transferForm, 'Source and destination accounts cannot be the same.');
      return;
    }
    
    try {
      const apiClient = new ApiClient();
      
      // Get current balance to validate transfer
      const account = await apiClient.getAccountDetails(fromAccountId);
      
      if (amount > account.balance) {
        showFormError(transferForm, 'Insufficient funds for transfer.');
        return;
      }
      
      const transaction = await apiClient.createTransfer(fromAccountId, toAccountId, amount, description);
      
      showFormSuccess(transferForm, 'Transfer successful!');
      
      // Reset form
      transferForm.reset();
      
      // Close modal
      const modal = document.getElementById('transfer-modal');
      if (modal) {
        modal.classList.add('hidden');
      }
      
      // Refresh the page after a delay to show updated balance
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      console.error('Transfer failed:', error);
      showFormError(transferForm, 'Transfer failed. Please try again.');
    }
  });
}

async function populateAccountDropdown(): Promise<void> {
  const toAccountDropdown = document.querySelector('#transfer-form [name="to_account_id"]') as HTMLSelectElement;
  const fromAccountDropdown = document.querySelector('#transfer-form [name="from_account_id"]') as HTMLSelectElement;
  
  if (!toAccountDropdown || !fromAccountDropdown) return;
  
  try {
    const apiClient = new ApiClient();
    const accounts = await apiClient.getAccounts();
    
    // Clear existing options except the placeholder
    while (toAccountDropdown.options.length > 1) {
      toAccountDropdown.remove(1);
    }
    
    while (fromAccountDropdown.options.length > 1) {
      fromAccountDropdown.remove(1);
    }
    
    // Add accounts to the dropdown
    accounts.forEach(account => {
      const option = document.createElement('option');
      option.value = account.id;
      option.textContent = `${account.name} (${formatCurrency(account.balance, account.currency)})`;
      
      const fromOption = option.cloneNode(true) as HTMLOptionElement;
      
      toAccountDropdown.appendChild(option);
      fromAccountDropdown.appendChild(fromOption);
    });
  } catch (error) {
    console.error('Failed to load accounts for transfer:', error);
  }
}

function setupCloseModalButtons(): void {
  const closeButtons = document.querySelectorAll('.modal-close-btn');
  closeButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Find parent modal
      const modal = (button as HTMLElement).closest('.modal');
      if (modal) {
        modal.classList.add('hidden');
        
        // Reset form errors
        const form = modal.querySelector('form');
        if (form) {
          const errorElement = form.querySelector('.error-message');
          const successElement = form.querySelector('.success-message');
          
          if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.add('hidden');
          }
          
          if (successElement) {
            successElement.textContent = '';
            successElement.classList.add('hidden');
          }
        }
      }
    });
  });
  
  // Close modal when clicking outside
  const modals = document.querySelectorAll('.modal');
  modals.forEach(modal => {
    modal.addEventListener('click', (event) => {
      if (event.target === modal) {
        modal.classList.add('hidden');
      }
    });
  });
  
  // Close modal with Escape key
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      const openModal = document.querySelector('.modal:not(.hidden)');
      if (openModal) {
        openModal.classList.add('hidden');
      }
    }
  });
}

// Helper functions
function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency 
  }).format(amount);
}

function showFormError(form: HTMLFormElement, message: string): void {
  const errorElement = form.querySelector('.error-message');
  const successElement = form.querySelector('.success-message');
  
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
  }
  
  if (successElement) {
    successElement.textContent = '';
    successElement.classList.add('hidden');
  }
}

function showFormSuccess(form: HTMLFormElement, message: string): void {
  const errorElement = form.querySelector('.error-message');
  const successElement = form.querySelector('.success-message');
  
  if (successElement) {
    successElement.textContent = message;
    successElement.classList.remove('hidden');
  }
  
  if (errorElement) {
    errorElement.textContent = '';
    errorElement.classList.add('hidden');
  }
}