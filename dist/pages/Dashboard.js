var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { accountService } from '../services/api/accountService';
import { transactionService } from '../services/api/transactionService';
import { authService } from '../services/api/authService';
const Dashboard = () => {
    const [accounts, setAccounts] = useState([]);
    const [selectedAccount, setSelectedAccount] = useState(null);
    const [transactions, setTransactions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    // For transfer functionality
    const [recipientUsername, setRecipientUsername] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [transferAmount, setTransferAmount] = useState('');
    const [selectedRecipient, setSelectedRecipient] = useState(null);
    const [transferSuccess, setTransferSuccess] = useState('');
    const navigate = useNavigate();
    // Load user accounts
    useEffect(() => {
        const fetchAccounts = () => __awaiter(void 0, void 0, void 0, function* () {
            try {
                const userAccounts = yield accountService.getUserAccounts();
                setAccounts(userAccounts);
                // If we have accounts, select the first one by default
                if (userAccounts.length > 0) {
                    setSelectedAccount(userAccounts[0]);
                }
            }
            catch (err) {
                setError('Failed to load accounts');
                console.error('Error loading accounts:', err);
            }
            finally {
                setIsLoading(false);
            }
        });
        fetchAccounts();
    }, []);
    // Load transactions when selected account changes
    useEffect(() => {
        if (selectedAccount) {
            const fetchTransactions = () => __awaiter(void 0, void 0, void 0, function* () {
                try {
                    const accountTransactions = yield transactionService.getAccountTransactions(selectedAccount.account_id);
                    setTransactions(accountTransactions);
                }
                catch (err) {
                    console.error('Error loading transactions:', err);
                }
            });
            fetchTransactions();
        }
        else {
            setTransactions([]);
        }
    }, [selectedAccount]);
    const handleAccountChange = (e) => {
        const accountId = Number(e.target.value);
        const account = accounts.find(acc => acc.account_id === accountId) || null;
        setSelectedAccount(account);
    };
    const handleSearch = () => __awaiter(void 0, void 0, void 0, function* () {
        if (!recipientUsername)
            return;
        try {
            const results = yield accountService.searchAccounts(recipientUsername);
            setSearchResults(results);
            setSelectedRecipient(null); // Clear previous selection
        }
        catch (err) {
            console.error('Error searching accounts:', err);
            setSearchResults([]);
        }
    });
    const handleTransfer = (e) => __awaiter(void 0, void 0, void 0, function* () {
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
            yield accountService.transferMoney(selectedAccount.account_id, {
                amount,
                recipient_account_id: selectedRecipient.account_id,
                description: `Transfer to ${selectedRecipient.username || 'account'}`
            });
            // Refresh accounts to show updated balance
            const userAccounts = yield accountService.getUserAccounts();
            setAccounts(userAccounts);
            // Update selected account with refreshed data
            const updatedSelectedAccount = userAccounts.find(acc => acc.account_id === selectedAccount.account_id) || null;
            setSelectedAccount(updatedSelectedAccount);
            // Refresh transactions
            if (updatedSelectedAccount) {
                const accountTransactions = yield transactionService.getAccountTransactions(updatedSelectedAccount.account_id);
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
        }
        catch (err) {
            setError('Transfer failed');
            console.error('Error making transfer:', err);
        }
    });
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
        return _jsx("div", Object.assign({ className: "flex justify-center items-center h-screen" }, { children: "Loading..." }));
    }
    return (_jsxs("div", Object.assign({ className: "container mx-auto p-4" }, { children: [_jsxs("header", Object.assign({ className: "flex justify-between items-center mb-8" }, { children: [_jsx("h1", Object.assign({ className: "text-2xl font-bold" }, { children: "Banking Dashboard" })), _jsx("button", Object.assign({ onClick: handleLogout, className: "bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600" }, { children: "Logout" }))] })), error && (_jsx("div", Object.assign({ className: "bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" }, { children: error }))), transferSuccess && (_jsx("div", Object.assign({ className: "bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4" }, { children: transferSuccess }))), _jsxs("div", Object.assign({ className: "grid grid-cols-1 md:grid-cols-3 gap-6" }, { children: [_jsxs("div", Object.assign({ className: "col-span-1 bg-white p-6 rounded-lg shadow" }, { children: [_jsx("h2", Object.assign({ className: "text-xl font-semibold mb-4" }, { children: "Your Accounts" })), accounts.length === 0 ? (_jsxs("div", Object.assign({ className: "text-gray-500" }, { children: [_jsx("p", { children: "You don't have any accounts yet." }), _jsx(Link, Object.assign({ to: "/create-account", className: "inline-block mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" }, { children: "Create Account" }))] }))) : (_jsxs(_Fragment, { children: [_jsxs("div", Object.assign({ className: "mb-4" }, { children: [_jsx("label", Object.assign({ className: "block text-gray-700 text-sm font-bold mb-2" }, { children: "Select Account" })), _jsx("select", Object.assign({ className: "w-full px-3 py-2 border border-gray-300 rounded", value: (selectedAccount === null || selectedAccount === void 0 ? void 0 : selectedAccount.account_id) || '', onChange: handleAccountChange }, { children: accounts.map(account => (_jsxs("option", Object.assign({ value: account.account_id }, { children: [account.account_type, " - ", account.currency_code] }), account.account_id))) }))] })), selectedAccount && (_jsxs("div", Object.assign({ className: "border-t pt-4" }, { children: [_jsx("h3", Object.assign({ className: "font-semibold" }, { children: "Account Details" })), _jsxs("p", Object.assign({ className: "text-gray-700" }, { children: ["Type: ", selectedAccount.account_type] })), _jsxs("p", Object.assign({ className: "text-gray-700" }, { children: ["Currency: ", selectedAccount.currency_code] })), _jsxs("p", Object.assign({ className: "text-xl font-bold mt-2" }, { children: ["Balance: ", selectedAccount.balance.toFixed(2), " ", selectedAccount.currency_code] }))] }))), _jsx("div", Object.assign({ className: "mt-4" }, { children: _jsx(Link, Object.assign({ to: "/create-account", className: "inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" }, { children: "Create New Account" })) }))] }))] })), _jsxs("div", Object.assign({ className: "col-span-1 bg-white p-6 rounded-lg shadow" }, { children: [_jsx("h2", Object.assign({ className: "text-xl font-semibold mb-4" }, { children: "Make a Transfer" })), !selectedAccount ? (_jsx("p", Object.assign({ className: "text-gray-500" }, { children: "Please select an account to make a transfer." }))) : (_jsxs("form", Object.assign({ onSubmit: handleTransfer }, { children: [_jsxs("div", Object.assign({ className: "mb-4" }, { children: [_jsx("label", Object.assign({ className: "block text-gray-700 text-sm font-bold mb-2" }, { children: "Recipient Username" })), _jsxs("div", Object.assign({ className: "flex" }, { children: [_jsx("input", { type: "text", className: "flex-grow px-3 py-2 border border-gray-300 rounded-l", value: recipientUsername, onChange: (e) => setRecipientUsername(e.target.value), placeholder: "Enter username" }), _jsx("button", Object.assign({ type: "button", className: "bg-gray-200 text-gray-700 px-4 py-2 rounded-r hover:bg-gray-300", onClick: handleSearch }, { children: "Search" }))] }))] })), searchResults.length > 0 && (_jsxs("div", Object.assign({ className: "mb-4" }, { children: [_jsx("label", Object.assign({ className: "block text-gray-700 text-sm font-bold mb-2" }, { children: "Select Recipient Account" })), _jsxs("select", Object.assign({ className: "w-full px-3 py-2 border border-gray-300 rounded", value: (selectedRecipient === null || selectedRecipient === void 0 ? void 0 : selectedRecipient.account_id) || '', onChange: (e) => {
                                                    const accountId = Number(e.target.value);
                                                    const account = searchResults.find(acc => acc.account_id === accountId) || null;
                                                    setSelectedRecipient(account);
                                                } }, { children: [_jsx("option", Object.assign({ value: "" }, { children: "Select an account" })), searchResults.map(account => (_jsxs("option", Object.assign({ value: account.account_id }, { children: [account.username, " - ", account.account_type, " (", account.currency_code, ")"] }), account.account_id)))] }))] }))), _jsxs("div", Object.assign({ className: "mb-4" }, { children: [_jsxs("label", Object.assign({ className: "block text-gray-700 text-sm font-bold mb-2" }, { children: ["Amount (", selectedAccount.currency_code, ")"] })), _jsx("input", { type: "number", step: "0.01", min: "0.01", className: "w-full px-3 py-2 border border-gray-300 rounded", value: transferAmount, onChange: (e) => setTransferAmount(e.target.value), placeholder: "Enter amount" })] })), _jsx("button", Object.assign({ type: "submit", className: "w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600", disabled: !selectedRecipient || !transferAmount }, { children: "Transfer Funds" }))] })))] })), _jsxs("div", Object.assign({ className: "col-span-1 bg-white p-6 rounded-lg shadow" }, { children: [_jsx("h2", Object.assign({ className: "text-xl font-semibold mb-4" }, { children: "Recent Transactions" })), !selectedAccount ? (_jsx("p", Object.assign({ className: "text-gray-500" }, { children: "Please select an account to view transactions." }))) : transactions.length === 0 ? (_jsx("p", Object.assign({ className: "text-gray-500" }, { children: "No transactions found for this account." }))) : (_jsxs("div", Object.assign({ className: "divide-y" }, { children: [transactions.slice(0, 5).map(transaction => (_jsxs("div", Object.assign({ className: "py-3" }, { children: [_jsxs("div", Object.assign({ className: "flex justify-between" }, { children: [_jsx("span", Object.assign({ className: "font-medium" }, { children: transaction.description })), _jsxs("span", Object.assign({ className: `font-semibold ${transaction.amount > 0 ? 'text-green-600' : 'text-red-600'}` }, { children: [transaction.amount > 0 ? '+' : '', transaction.amount.toFixed(2), " ", selectedAccount.currency_code] }))] })), _jsx("div", Object.assign({ className: "text-sm text-gray-500" }, { children: new Date(transaction.date_posted).toLocaleDateString() }))] }), transaction.transaction_id))), _jsx("div", Object.assign({ className: "pt-4" }, { children: _jsx(Link, Object.assign({ to: `/transactions/${selectedAccount.account_id}`, className: "text-blue-500 hover:text-blue-700" }, { children: "View all transactions \u2192" })) }))] })))] }))] }))] })));
};
export default Dashboard;
