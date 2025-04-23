"""
Core gRPC server implementation for the banking system.
This module provides the base server and service implementation.
"""

import concurrent.futures
import logging
import time
import grpc
from grpc_reflection.v1alpha import reflection
import os
import sys

# Import generated gRPC modules
sys.path.append('./grpc_utils')  # Add the path to generated modules

# Import gRPC service implementations
from grpc_services.user_service import UserServiceServicer
from grpc_services.account_service import AccountServiceServicer
from grpc_services.transaction_service import TransactionServiceServicer
from grpc_services.marketplace_service import MarketplaceServiceServicer

# Import generated gRPC code
from proto import user_service_pb2, user_service_pb2_grpc
from proto import account_service_pb2, account_service_pb2_grpc
from proto import transaction_service_pb2, transaction_service_pb2_grpc
from proto import marketplace_service_pb2, marketplace_service_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GrpcServer:
    """Base gRPC server that can host multiple services."""
    
    def __init__(self, address='[::]:50051', max_workers=10):
        """Initialize the gRPC server.
        
        Args:
            address: The server address in the format 'host:port'
            max_workers: Maximum number of worker threads
        """
        self.address = address
        self.max_workers = max_workers
        self.server = None
        self.services = {}
        self._is_running = False
        
    def add_service(self, service_name, service_class):
        """Add a service to the server.
        
        Args:
            service_name: The full name of the service (package.ServiceName)
            service_class: The service class implementation
        """
        self.services[service_name] = service_class
        logger.info(f"Added service: {service_name}")
        
    def start(self):
        """Start the gRPC server."""
        self.server = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        )
        
        # Add all registered services
        service_names = []
        for service_name, service_class in self.services.items():
            service_class.add_to_server(self.server)
            service_names.append(service_name)
            logger.info(f"Registered service: {service_name}")
        
        # Add reflection service
        service_names.append(reflection.SERVICE_NAME)
        reflection.enable_server_reflection(service_names, self.server)
        
        # Start the server
        self.server.add_insecure_port(self.address)
        self.server.start()
        self._is_running = True
        logger.info(f"Server started on {self.address}")
        
    def stop(self, grace=None):
        """Stop the gRPC server.
        
        Args:
            grace: Optional grace period for clean shutdown
        """
        if self.server is not None:
            logger.info("Stopping server...")
            self.server.stop(grace)
            self._is_running = False
            logger.info("Server stopped")
            
    def wait_for_termination(self):
        """Block until the server terminates."""
        if self.server is not None:
            self.server.wait_for_termination()
            
    def serve_forever(self):
        """Start the server and block until it terminates."""
        self.start()
        try:
            self.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("Server interrupted")
            self.stop(5)  # 5 seconds grace period

def health_check_response(context):
    """Generate a health check response.
    
    Args:
        context: The gRPC context
        
    Returns:
        A dictionary with server health status
    """
    return {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    }

def serve():
    """Start gRPC server with all banking services"""
    # Create a gRPC server
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    
    # Add services to the server
    user_service_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceServicer(), server)
    
    account_service_pb2_grpc.add_AccountServiceServicer_to_server(
        AccountServiceServicer(), server)
    
    transaction_service_pb2_grpc.add_TransactionServiceServicer_to_server(
        TransactionServiceServicer(), server)
    
    marketplace_service_pb2_grpc.add_MarketplaceServiceServicer_to_server(
        MarketplaceServiceServicer(), server)
    
    # Enable reflection for tools like grpcurl
    SERVICE_NAMES = (
        user_service_pb2.DESCRIPTOR.services_by_name['UserService'].full_name,
        account_service_pb2.DESCRIPTOR.services_by_name['AccountService'].full_name,
        transaction_service_pb2.DESCRIPTOR.services_by_name['TransactionService'].full_name,
        marketplace_service_pb2.DESCRIPTOR.services_by_name['MarketplaceService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Define port
    port = os.environ.get('GRPC_PORT', '50051')
    server.add_insecure_port(f'[::]:{port}')
    
    # Start the server
    server.start()
    logger.info(f"gRPC server started on port {port}")
    
    # Keep the server running
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()