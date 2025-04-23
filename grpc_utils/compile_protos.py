#!/usr/bin/env python3
"""
Proto compiler utility to generate Python code from .proto files
"""
import os
import subprocess
import sys

def generate_proto_code():
    """Generate Python code from proto files"""
    proto_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'proto')
    output_dir = os.path.dirname(proto_dir)
    
    if not os.path.exists(proto_dir):
        print(f"Proto directory not found: {proto_dir}")
        return False
    
    # Get all proto files
    proto_files = [f for f in os.listdir(proto_dir) if f.endswith('.proto')]
    
    if not proto_files:
        print(f"No proto files found in {proto_dir}")
        return False
    
    print(f"Found {len(proto_files)} proto files: {', '.join(proto_files)}")
    
    # Generate Python code for each proto file
    for proto_file in proto_files:
        proto_path = os.path.join(proto_dir, proto_file)
        cmd = [
            'python', '-m', 'grpc_tools.protoc',
            f'--proto_path={proto_dir}',
            f'--python_out={output_dir}',
            f'--grpc_python_out={output_dir}',
            proto_path
        ]
        
        try:
            print(f"Generating code for {proto_file}...")
            subprocess.check_call(cmd)
            print(f"Successfully generated code for {proto_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating code for {proto_file}: {e}")
            return False
    
    print("All proto files compiled successfully")
    return True

if __name__ == '__main__':
    success = generate_proto_code()
    sys.exit(0 if success else 1)