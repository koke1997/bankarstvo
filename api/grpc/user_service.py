import grpc
import logging
from concurrent import futures
import sys
import os
import time
import uuid

# Import generated gRPC code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import user_service_pb2, user_service_pb2_grpc

# Import database models and handlers
from utils.extensions import db, bcrypt
from core.models import User

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
            first_name = request.first_name if hasattr(request, 'first_name') else None
            last_name = request.last_name if hasattr(request, 'last_name') else None
            phone_number = request.phone_number if hasattr(request, 'phone_number') else None
            address = request.address if hasattr(request, 'address') else None
            
            # Check if user already exists - use db.session.query instead of User.query
            existing_user = db.session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                message = "Username or email already exists"
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(message)
                return user_service_pb2.UserResponse(
                    success=False,
                    message=message
                )
                
            # Create new user - use only the attributes that are present in the User model
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=f"{first_name or ''} {last_name or ''}".strip()
            )
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            # Prepare user response (excluding sensitive fields)
            # Ensure we only access fields that exist in the User model
            user_proto = user_service_pb2.User(
                user_id=user.user_id,
                username=user.username,
                email=user.email
            )
            
            # Add optional fields if they exist in both the model and the proto
            if hasattr(user_service_pb2.User, 'date_created') and hasattr(user, 'account_created'):
                user_proto.date_created = str(user.account_created)
            
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
            
            # Find user by username or email - use db.session.query instead of User.query
            user = db.session.query(User).filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()
            
            if not user or not bcrypt.check_password_hash(user.password_hash, password):
                message = "Invalid username/email or password"
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
            # Ensure we only access fields that exist in the User model
            user_proto = user_service_pb2.User(
                user_id=user.user_id,
                username=user.username,
                email=user.email
            )
            
            # Add optional fields if they exist in both the model and the proto
            if hasattr(user_service_pb2.User, 'date_created') and hasattr(user, 'account_created'):
                user_proto.date_created = str(user.account_created)
            
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
            
            # Get user from database - use db.session.query instead of User.query
            user = db.session.query(User).get(user_id)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return user_service_pb2.UserResponse(
                    success=False,
                    message="User not found"
                )
            
            # Prepare user response (excluding sensitive fields)
            # Ensure we only access fields that exist in the User model
            user_proto = user_service_pb2.User(
                user_id=user.user_id,
                username=user.username,
                email=user.email
            )
            
            # Add optional fields if they exist in both the model and the proto
            if hasattr(user_service_pb2.User, 'date_created') and hasattr(user, 'account_created'):
                user_proto.date_created = str(user.account_created)
            
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
            # Only include fields that exist in the User model
            if request.HasField('email'):
                fields_to_update['email'] = request.email
                
            # Update full_name field if first_name or last_name is provided
            if (request.HasField('first_name') or request.HasField('last_name')):
                # Get the user first to preserve existing name components
                user = db.session.query(User).get(user_id)
                if not user:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("User not found")
                    return user_service_pb2.UserResponse(
                        success=False,
                        message="User not found"
                    )
                    
                # Get current name parts if available
                current_name = user.full_name or ""
                current_parts = current_name.split(" ", 1)
                current_first = current_parts[0] if len(current_parts) > 0 else ""
                current_last = current_parts[1] if len(current_parts) > 1 else ""
                
                # Update with new values if provided
                first = request.first_name if request.HasField('first_name') else current_first
                last = request.last_name if request.HasField('last_name') else current_last
                
                fields_to_update['full_name'] = f"{first} {last}".strip()
            
            # Update password if provided
            if request.HasField('password') and request.password:
                fields_to_update['password_hash'] = bcrypt.generate_password_hash(request.password).decode('utf-8')
            
            # Check if there's anything to update
            if not fields_to_update:
                return user_service_pb2.UserResponse(
                    success=True,
                    message="No fields to update"
                )
                
            # Get user from database if not already fetched
            if 'user' not in locals():
                user = db.session.query(User).get(user_id)
                
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return user_service_pb2.UserResponse(
                    success=False,
                    message="User not found"
                )
            
            # Update user in database
            for key, value in fields_to_update.items():
                setattr(user, key, value)
                
            db.session.commit()
            
            # Prepare user response (excluding sensitive fields)
            user_proto = user_service_pb2.User(
                user_id=user.user_id,
                username=user.username,
                email=user.email
            )
            
            # Add optional fields if they exist
            if hasattr(user_service_pb2.User, 'date_created') and hasattr(user, 'account_created'):
                user_proto.date_created = str(user.account_created)
            
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