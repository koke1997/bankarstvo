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
// Transaction service functions
export const transactionService = {
    // Get transactions for a specific account
    getAccountTransactions: (accountId, filter) => __awaiter(void 0, void 0, void 0, function* () {
        let url = `/accounts/${accountId}/transactions`;
        if (filter) {
            const params = new URLSearchParams();
            if (filter.startDate)
                params.append('startDate', filter.startDate);
            if (filter.endDate)
                params.append('endDate', filter.endDate);
            if (filter.type)
                params.append('type', filter.type);
            if (filter.minAmount)
                params.append('minAmount', filter.minAmount.toString());
            if (filter.maxAmount)
                params.append('maxAmount', filter.maxAmount.toString());
            if (params.toString()) {
                url += `?${params.toString()}`;
            }
        }
        const response = yield apiClient.get(url);
        return response.data;
    }),
    // Get details of a specific transaction
    getTransactionDetails: (transactionId) => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.get(`/transactions/${transactionId}`);
        return response.data;
    }),
    // Get a transaction receipt or PDF
    getTransactionReceipt: (transactionId) => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.get(`/transactions/${transactionId}/receipt`, {
            responseType: 'blob'
        });
        return response.data;
    })
};
export default transactionService;
