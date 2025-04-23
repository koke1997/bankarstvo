import grpc
import logging
from concurrent import futures
from DatabaseHandling.authentication import authenticate_user
from DatabaseHandling.registration_func import register_user
import sys
import os
import time
import uuid

# Import generated gRPC code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import user_service_pb2, user_service_pb2_grpc

# Import database models and handlers
from DatabaseHandling.connection import get_db_connection
from DatabaseHandling.authentication import authenticate_user, hash_password
from DatabaseHandling.registration_func import register_user
from core.models import UserModel

logger = logging.getLogger(__name__)

class UserServicer(user_service_pb2_grpc.UserServiceServicer):
    """Implementation of UserService service."""

    def Register(self, request, context):
        """Register a new user."""
        try:
            # Extract fields from request
            username = request.username
            email = request.email
            password = request.password
            first_name = request.first_name
            last_name = request.last_name
            phone_number = request.phone_number
            address = request.address
            
            # Process registration
            db_connection = get_db_connection()
            success, message, user = register_user(
                db_connection, 
                username, 
                email, 
                password, 
                first_name, 
                last_name, 
                phone_number, 
                address
            )
            
            if not success:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(message)
                return user_service_pb2.UserResponse(
                    success=False,
                    message=message
                )
            
            # Prepare user response (excluding sensitive fields)
            user_proto = user_service_pb2.User(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number or "",
                address=user.address or "",
                date_created=str(user.date_created),
                is_active=user.is_active,
                profile_picture_url=user.profile_picture_url or ""
            )
            
            return user_service_pb2.UserResponse(
                success=True,
                message="User registered successfully",
                user=user_proto
            )
            
        except Exception as e:
            logging.error(f"Error registering user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error registering user: {str(e)}")
            return user_service_pb2.UserResponse(
                success=False,
                message=f"Failed to register user: {str(e)}"
            )

    def Authenticate(self, request, context):
        """Authenticate a user and generate a token."""
        try:
            # Extract fields from request
            username_or_email = request.username_or_email
            password = request.password
            
            # Authenticate user
            db_connection = get_db_connection()
            success, message, user = authenticate_user(
                db_connection, username_or_email, password
            )
            
            if not success:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(message)
                return user_service_pb2.AuthResponse(
                    success=False,
                    message=message
                )
            
            # Generate a token (in a real system, use JWT or similar)
            # Here we're just creating a dummy token for demonstration
            token = str(uuid.uuid4())
            
            # Prepare user response (excluding sensitive fields)
            user_proto = user_service_pb2.User(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number or "",
                address=user.address or "",
                date_created=str(user.date_created),
                is_active=user.is_active,
                profile_picture_url=user.profile_picture_url or ""
            )
            
            return user_service_pb2.AuthResponse(
                success=True,
                message="Authentication successful",
                token=token,
                user=user_proto
            )
            
        except Exception as e:
            logging.error(f"Error authenticating user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error authenticating user: {str(e)}")
            return user_service_pb2.AuthResponse(
                success=False,
                message=f"Failed to authenticate user: {str(e)}"
            )
    
    def GetUser(self, request, context):
        """Get user details by ID."""
        try:
            # Extract fields from request
            user_id = request.user_id
            
            # Get user from database
            db_connection = get_db_connection()
            user = UserModel.find_by_id(db_connection, user_id)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return user_service_pb2.UserResponse(
                    success=False,
                    message="User not found"
                )
            
            # Prepare user response (excluding sensitive fields)
            user_proto = user_service_pb2.User(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number or "",
                address=user.address or "",
                date_created=str(user.date_created),
                is_active=user.is_active,
                profile_picture_url=user.profile_picture_url or ""
            )
            
            return user_service_pb2.UserResponse(
                success=True,
                message="User retrieved successfully",
                user=user_proto
            )
            
        except Exception as e:
            logging.error(f"Error retrieving user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving user: {str(e)}")
            return user_service_pb2.UserResponse(
                success=False,
                message=f"Failed to retrieve user: {str(e)}"
            )
    
    def UpdateUser(self, request, context):
        """Update user details."""
        try:
            # Extract fields from request
            user_id = request.user_id
            fields_to_update = {}
            
            # Check which fields are set and add them to the update dict
            if request.HasField('email'):
                fields_to_update['email'] = request.email
            if request.HasField('first_name'):
                fields_to_update['first_name'] = request.first_name
            if request.HasField('last_name'):
                fields_to_update['last_name'] = request.last_name
            if request.HasField('phone_number'):
                fields_to_update['phone_number'] = request.phone_number
            if request.HasField('address'):
                fields_to_update['address'] = request.address
            if request.HasField('profile_picture_url'):
                fields_to_update['profile_picture_url'] = request.profile_picture_url
            
            # Update password if provided
            if request.HasField('password') and request.password:
                fields_to_update['password_hash'] = hash_password(request.password)
            
            # Check if there's anything to update
            if not fields_to_update:
                return user_service_pb2.UserResponse(
                    success=True,
                    message="No fields to update"
                )
                
            # Get user from database
            db_connection = get_db_connection()
            user = UserModel.find_by_id(db_connection, user_id)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return user_service_pb2.UserResponse(
                    success=False,
                    message="User not found"
                )
            
            # Update user in database
            success = user.update(db_connection, **fields_to_update)
            
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to update user")
                return user_service_pb2.UserResponse(
                    success=False,
                    message="Failed to update user"
                )
            
            # Get updated user
            updated_user = UserModel.find_by_id(db_connection, user_id)
            
            # Prepare user response (excluding sensitive fields)
            user_proto = user_service_pb2.User(
                user_id=updated_user.user_id,
                username=updated_user.username,
                email=updated_user.email,
                first_name=updated_user.first_name,
                last_name=updated_user.last_name,
                phone_number=updated_user.phone_number or "",
                address=updated_user.address or "",
                date_created=str(updated_user.date_created),
                is_active=updated_user.is_active,
                profile_picture_url=updated_user.profile_picture_url or ""
            )
            
            return user_service_pb2.UserResponse(
                success=True,
                message="User updated successfully",
                user=user_proto
            )
            
        except Exception as e:
            logging.error(f"Error updating user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating user: {str(e)}")
            return user_service_pb2.UserResponse(
                success=False,
                message=f"Failed to update user: {str(e)}"
            )

def serve():
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(
        UserServicer(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    print("User gRPC server started on port 50053")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)
        print("Server stopped")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()