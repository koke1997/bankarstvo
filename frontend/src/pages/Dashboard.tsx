import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { accountService, Account } from '../services/api/accountService';
import { transactionService, Transaction } from '../services/api/transactionService';
import { authService } from '../services/api/authService';

const Dashboard: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // For transfer functionality
  const [recipientUsername, setRecipientUsername] = useState('');
  const [searchResults, setSearchResults] = useState<Account[]>([]);
  const [transferAmount, setTransferAmount] = useState('');
  const [selectedRecipient, setSelectedRecipient] = useState<Account | null>(null);
  const [transferSuccess, setTransferSuccess] = useState('');
  
  const navigate = useNavigate();

  // Load user accounts
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const userAccounts = await accountService.getUserAccounts();
        setAccounts(userAccounts);
        
        // If we have accounts, select the first one by default
        if (userAccounts.length > 0) {
          setSelectedAccount(userAccounts[0]);
        }
      } catch (err) {
        setError('Failed to load accounts');
        console.error('Error loading accounts:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  // Load transactions when selected account changes
  useEffect(() => {
    if (selectedAccount) {
      const fetchTransactions = async () => {
        try {
          const accountTransactions = await transactionService.getAccountTransactions(selectedAccount.account_id);
          setTransactions(accountTransactions);
        } catch (err) {
          console.error('Error loading transactions:', err);
        }
      };

      fetchTransactions();
    } else {
      setTransactions([]);
    }
  }, [selectedAccount]);

  const handleAccountChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const accountId = Number(e.target.value);
    const account = accounts.find(acc => acc.account_id === accountId) || null;
    setSelectedAccount(account);
  };

  const handleSearch = async () => {
    if (!recipientUsername) return;
    
    try {
      const results = await accountService.searchAccounts(recipientUsername);
      setSearchResults(results);
      setSelectedRecipient(null); // Clear previous selection
    } catch (err) {
      console.error('Error searching accounts:', err);
      setSearchResults([]);
    }
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedAccount || !selectedRecipient || !transferAmount) {
      return;
    }
    
    try {
      const amount = parseFloat(transferAmount);
      if (isNaN(amount) || amount <= 0) {
        setError('Please enter a valid amount');
        return;
      }
      
      await accountService.transferMoney(selectedAccount.account_id, {
        amount,
        recipient_account_id: selectedRecipient.account_id,
        description: `Transfer to ${selectedRecipient.username || 'account'}`
      });
      
      // Refresh accounts to show updated balance
      const userAccounts = await accountService.getUserAccounts();
      setAccounts(userAccounts);
      
      // Update selected account with refreshed data
      const updatedSelectedAccount = userAccounts.find(acc => acc.account_id === selectedAccount.account_id) || null;
      setSelectedAccount(updatedSelectedAccount);
      
      // Refresh transactions
      if (updatedSelectedAccount) {
        const accountTransactions = await transactionService.getAccountTransactions(updatedSelectedAccount.account_id);
        setTransactions(accountTransactions);
      }
      
      // Show success message and reset form
      setTransferSuccess('Transfer successful!');
      setTransferAmount('');
      setSelectedRecipient(null);
      setSearchResults([]);
      setRecipientUsername('');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setTransferSuccess('');
      }, 3000);
    } catch (err) {
      setError('Transfer failed');
      console.error('Error making transfer:', err);
    }
  };

  const handleLogout = () => {
    authService.logout()
      .then(() => {
        navigate('/login');
      })
      .catch(err => {
        console.error('Logout error:', err);
        // Still remove token and redirect even if API call fails
        authService.removeToken();
        navigate('/login');
      });
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Banking Dashboard</h1>
        <button 
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </header>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {transferSuccess && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {transferSuccess}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Account Selection Section */}
        <div className="col-span-1 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Your Accounts</h2>
          
          {accounts.length === 0 ? (
            <div className="text-gray-500">
              <p>You don't have any accounts yet.</p>
              <Link 
                to="/create-account" 
                className="inline-block mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Create Account
              </Link>
            </div>
          ) : (
            <>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Select Account
                </label>
                <select 
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                  value={selectedAccount?.account_id || ''}
                  onChange={handleAccountChange}
                >
                  {accounts.map(account => (
                    <option key={account.account_id} value={account.account_id}>
                      {account.account_type} - {account.currency_code}
                    </option>
                  ))}
                </select>
              </div>
              
              {selectedAccount && (
                <div className="border-t pt-4">
                  <h3 className="font-semibold">Account Details</h3>
                  <p className="text-gray-700">Type: {selectedAccount.account_type}</p>
                  <p className="text-gray-700">Currency: {selectedAccount.currency_code}</p>
                  <p className="text-xl font-bold mt-2">
                    Balance: {selectedAccount.balance.toFixed(2)} {selectedAccount.currency_code}
                  </p>
                </div>
              )}
              
              <div className="mt-4">
                <Link 
                  to="/create-account" 
                  className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  Create New Account
                </Link>
              </div>
            </>
          )}
        </div>
        
        {/* Transfer Section */}
        <div className="col-span-1 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Make a Transfer</h2>
          
          {!selectedAccount ? (
            <p className="text-gray-500">Please select an account to make a transfer.</p>
          ) : (
            <form onSubmit={handleTransfer}>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Recipient Username
                </label>
                <div className="flex">
                  <input
                    type="text"
                    className="flex-grow px-3 py-2 border border-gray-300 rounded-l"
                    value={recipientUsername}
                    onChange={(e) => setRecipientUsername(e.target.value)}
                    placeholder="Enter username"
                  />
                  <button
                    type="button"
                    className="bg-gray-200 text-gray-700 px-4 py-2 rounded-r hover:bg-gray-300"
                    onClick={handleSearch}
                  >
                    Search
                  </button>
                </div>
              </div>
              
              {searchResults.length > 0 && (
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Select Recipient Account
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                    value={selectedRecipient?.account_id || ''}
                    onChange={(e) => {
                      const accountId = Number(e.target.value);
                      const account = searchResults.find(acc => acc.account_id === accountId) || null;
                      setSelectedRecipient(account);
                    }}
                  >
                    <option value="">Select an account</option>
                    {searchResults.map(account => (
                      <option key={account.account_id} value={account.account_id}>
                        {account.username} - {account.account_type} ({account.currency_code})
                      </option>
                    ))}
                  </select>
                </div>
              )}
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Amount ({selectedAccount.currency_code})
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                  value={transferAmount}
                  onChange={(e) => setTransferAmount(e.target.value)}
                  placeholder="Enter amount"
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600"
                disabled={!selectedRecipient || !transferAmount}
              >
                Transfer Funds
              </button>
            </form>
          )}
        </div>
        
        {/* Recent Transactions Section */}
        <div className="col-span-1 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
          
          {!selectedAccount ? (
            <p className="text-gray-500">Please select an account to view transactions.</p>
          ) : transactions.length === 0 ? (
            <p className="text-gray-500">No transactions found for this account.</p>
          ) : (
            <div className="divide-y">
              {transactions.slice(0, 5).map(transaction => (
                <div key={transaction.transaction_id} className="py-3">
                  <div className="flex justify-between">
                    <span className="font-medium">{transaction.description}</span>
                    <span className={`font-semibold ${transaction.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {transaction.amount > 0 ? '+' : ''}{transaction.amount.toFixed(2)} {selectedAccount.currency_code}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(transaction.date_posted).toLocaleDateString()}
                  </div>
                </div>
              ))}
              
              <div className="pt-4">
                <Link 
                  to={`/transactions/${selectedAccount.account_id}`}
                  className="text-blue-500 hover:text-blue-700"
                >
                  View all transactions →
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;