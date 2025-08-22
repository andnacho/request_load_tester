"""
Request template management with random function support.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from .random_utils import process_random_functions


class RequestTemplate:
    """Represents a request template with name, description, and body."""
    
    def __init__(self, name: str, description: str, body: Dict[str, Any]):
        self.name = name
        self.description = description
        self.original_body = body  # Keep original for reference
        self.body = body  # This will be processed with random functions when needed
    
    def get_processed_body(self) -> Dict[str, Any]:
        """Get body with random functions processed (generates new values each time)."""
        return process_random_functions(self.original_body)


class TemplateLoader:
    """Loads and manages request templates."""
    
    def __init__(self, template_file: str = 'request-templates.json', template_filter: str = None):
        self.template_file = Path(__file__).parent.parent / template_file
        self.templates: List[RequestTemplate] = []
        self.all_templates: List[RequestTemplate] = []  # Keep track of all loaded templates
        self.template_filter = template_filter
        self.load_request_templates()
    
    def load_request_templates(self):
        """Load request templates from JSON file."""
        print('Loading request templates...')
        
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
            
            if 'templates' not in templates_data or not isinstance(templates_data['templates'], list):
                raise ValueError('Invalid template file format. Expected "templates" array.')
            
            # Load all templates first
            for template in templates_data['templates']:
                if 'request' in template:
                    template_obj = RequestTemplate(
                        name=template['name'],
                        description=template['description'],
                        body=template['request']
                    )
                    self.all_templates.append(template_obj)
            
            # Apply template filter if specified
            if self.template_filter:
                self.templates = self._filter_templates(self.all_templates, self.template_filter)
            else:
                self.templates = self.all_templates.copy()
            
            # Print loaded templates
            for template in self.templates:
                print(f"✓ Loaded template: {template.name} - {template.description}")
            
        except FileNotFoundError:
            print(f"❌ Could not load {self.template_file}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {self.template_file}: {e}")
            raise
        
        if not self.templates:
            if self.template_filter:
                print(f"❌ No templates match the filter: {self.template_filter}")
                print("Available templates:")
                for template in self.all_templates:
                    print(f"  - {template.name}")
                raise ValueError(f'No templates match the filter: {self.template_filter}')
            else:
                raise ValueError('No request templates could be loaded')
        
        print(f"\n📋 Loaded {len(self.templates)} request templates\n")
    
    def _filter_templates(self, templates: List[RequestTemplate], filter_str: str) -> List[RequestTemplate]:
        """
        Filter templates based on include/exclude patterns.
        
        Args:
            templates: List of all available templates
            filter_str: Filter string with include/exclude patterns
                       Examples: "template1,template2" (include only these)
                                "^template1" (exclude this one)  
                                "template1,^template2" (include template1, exclude template2)
        
        Returns:
            Filtered list of templates
        """
        if not filter_str:
            return templates
        
        # Parse filter string
        include_patterns = []
        exclude_patterns = []
        
        for pattern in filter_str.split(','):
            pattern = pattern.strip()
            if pattern.startswith('^'):
                exclude_patterns.append(pattern[1:])
            else:
                include_patterns.append(pattern)
        
        # Start with all templates if no include patterns, otherwise start with empty list
        if include_patterns:
            # Include mode: start with empty list and add matching templates
            filtered_templates = []
            for template in templates:
                if any(self._matches_pattern(template.name, pattern) for pattern in include_patterns):
                    filtered_templates.append(template)
        else:
            # No include patterns, start with all templates
            filtered_templates = templates.copy()
        
        # Apply exclude patterns
        if exclude_patterns:
            filtered_templates = [
                template for template in filtered_templates
                if not any(self._matches_pattern(template.name, pattern) for pattern in exclude_patterns)
            ]
        
        return filtered_templates
    
    def _matches_pattern(self, template_name: str, pattern: str) -> bool:
        """
        Check if template name matches the pattern.
        Supports exact match and simple wildcard matching.
        """
        # For now, use exact match
        # Could be extended to support wildcards (* and ?) if needed
        return template_name == pattern
    
    def get_random_template(self) -> RequestTemplate:
        """Get a random request template."""
        import random
        return random.choice(self.templates)
    
    def get_available_template_names(self) -> List[str]:
        """Get list of all available template names."""
        return [template.name for template in self.all_templates]
    
    def get_active_template_names(self) -> List[str]:
        """Get list of currently active (filtered) template names."""
        return [template.name for template in self.templates]
