var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import apiClient from './apiClient';
// Account service functions
export const accountService = {
    // Get all accounts for the current user
    getUserAccounts: () => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.get('/accounts');
        return response.data;
    }),
    // Get details of a specific account
    getAccountDetails: (accountId) => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.get(`/accounts/${accountId}`);
        return response.data;
    }),
    // Create a new account
    createAccount: (accountData) => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.post('/accounts', accountData);
        return response.data;
    }),
    // Transfer money between accounts
    transferMoney: (sourceAccountId, transferData) => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.post(`/accounts/${sourceAccountId}/transfer`, transferData);
        return response.data;
    }),
    // Get available currencies for account creation
    getAvailableCurrencies: () => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.get('/currencies');
        return response.data;
    }),
    // Search for accounts by username (for transfers)
    searchAccounts: (username) => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.get(`/search/accounts?username=${encodeURIComponent(username)}`);
        return response.data;
    })
};
export default accountService;
