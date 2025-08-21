"""
Request template management.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


class RequestTemplate:
    """Represents a request template with name, description, and body."""
    
    def __init__(self, name: str, description: str, body: Dict[str, Any]):
        self.name = name
        self.description = description
        self.body = body


class TemplateLoader:
    """Loads and manages request templates."""
    
    def __init__(self, template_file: str = 'request-templates.json'):
        self.template_file = Path(__file__).parent.parent / template_file
        self.templates: List[RequestTemplate] = []
        self.load_request_templates()
    
    def load_request_templates(self):
        """Load request templates from JSON file."""
        print('Loading request templates...')
        
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
            
            if 'templates' not in templates_data or not isinstance(templates_data['templates'], list):
                raise ValueError('Invalid template file format. Expected "templates" array.')
            
            for template in templates_data['templates']:
                if 'request' in template:
                    self.templates.append(RequestTemplate(
                        name=template['name'],
                        description=template['description'],
                        body=template['request']
                    ))
                    print(f"✓ Loaded template: {template['name']} - {template['description']}")
            
        except FileNotFoundError:
            print(f"❌ Could not load {self.template_file}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {self.template_file}: {e}")
            raise
        
        if not self.templates:
            raise ValueError('No request templates could be loaded')
        
        print(f"\n📋 Loaded {len(self.templates)} request templates\n")
    
    def get_random_template(self) -> RequestTemplate:
        """Get a random request template."""
        import random
        return random.choice(self.templates)
