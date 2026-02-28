"""Test that the sequential flow instructions are clear."""

from insurance_server_python.main import mcp
from insurance_server_python.widget_registry import TOOL_REGISTRY

tool = TOOL_REGISTRY['get-enhanced-quick-quote'].tool

print('✓ Server loaded successfully')
print('\n' + '='*80)
print('KEY SEQUENTIAL FLOW INSTRUCTIONS')
print('='*80)

lines = tool.description.split('\n')
for line in lines:
    if any(keyword in line for keyword in ['CRITICAL', 'STOP', 'STEP', 'WAIT']):
        print(line)

print('\n' + '='*80)
print('FULL DESCRIPTION')
print('='*80)
print(tool.description)
