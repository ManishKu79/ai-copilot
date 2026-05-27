import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import requests
from datetime import datetime

class DependencyScanner:
    def __init__(self):
        self.package_managers = {
            'python': {
                'files': ['requirements.txt', 'setup.py', 'Pipfile', 'pyproject.toml'],
                'pattern': r'^([a-zA-Z0-9_-]+)(?:[=<>~!]+)([0-9.]+)',
                'vulnerability_db': self._get_mock_vulnerabilities()
            },
            'node': {
                'files': ['package.json', 'package-lock.json', 'yarn.lock'],
                'pattern': r'"([@a-zA-Z0-9/_-]+)":\s*"[~^]?([0-9.]+)"',
                'vulnerability_db': self._get_mock_vulnerabilities()
            },
            'java': {
                'files': ['pom.xml', 'build.gradle'],
                'pattern': r'<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>',
                'vulnerability_db': self._get_mock_vulnerabilities()
            }
        }
        
        self.secret_patterns = {
            'API_KEY': r'(api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9]{16,})["\']',
            'AWS_KEY': r'(AKIA|ASIA)[A-Z0-9]{16}',
            'JWT_TOKEN': r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
            'PASSWORD': r'password\s*[=:]\s*["\']([^"\']+)["\']',
            'SECRET_KEY': r'secret[_]?key\s*[=:]\s*["\']([^"\']+)["\']',
            'DATABASE_URL': r'(postgresql|mysql|mongodb)://[^/\s]+',
            'PRIVATE_KEY': r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
            'TOKEN': r'token\s*[=:]\s*["\']([A-Za-z0-9_\-\.]+)["\']'
        }
        
        self.unsafe_imports = {
            'python': ['eval', 'exec', '__import__', 'os.system', 'subprocess.call', 'pickle.loads'],
            'javascript': ['eval', 'Function()', 'document.write', 'innerHTML', 'dangerouslySetInnerHTML'],
            'java': ['Runtime.exec', 'ProcessBuilder', 'Class.forName']
        }
    
    def _get_mock_vulnerabilities(self) -> Dict:
        """Mock vulnerability database (in production, would use actual APIs)"""
        return {
            'requests': {
                '<2.31.0': {
                    'severity': 'medium',
                    'cve': 'CVE-2023-12345',
                    'description': 'Potential information disclosure vulnerability',
                    'fix_version': '2.31.0'
                }
            },
            'django': {
                '<4.2.0': {
                    'severity': 'high',
                    'cve': 'CVE-2023-12346',
                    'description': 'SQL injection vulnerability',
                    'fix_version': '4.2.0'
                }
            },
            'express': {
                '<4.18.0': {
                    'severity': 'medium',
                    'cve': 'CVE-2022-12345',
                    'description': 'Prototype pollution vulnerability',
                    'fix_version': '4.18.0'
                }
            },
            'lodash': {
                '<4.17.21': {
                    'severity': 'high',
                    'cve': 'CVE-2021-12345',
                    'description': 'Command injection vulnerability',
                    'fix_version': '4.17.21'
                }
            },
            'axios': {
                '<1.6.0': {
                    'severity': 'medium',
                    'cve': 'CVE-2023-12347',
                    'description': 'Server-Side Request Forgery (SSRF)',
                    'fix_version': '1.6.0'
                }
            }
        }
    
    def scan_dependencies(self, repository_data: Dict) -> Dict:
        """Scan all dependencies in the repository"""
        files = repository_data.get('files_preview', [])
        structure = repository_data.get('structure', {})
        
        dependencies = []
        vulnerabilities = []
        outdated_packages = []
        
        # Scan for dependency files
        for file in files:
            file_name = file.get('name', '').lower()
            file_content = file.get('content_preview', '')
            
            # Python dependencies
            if file_name == 'requirements.txt':
                python_deps = self._parse_requirements_txt(file_content)
                dependencies.extend(python_deps)
                
                for dep in python_deps:
                    vuln = self._check_vulnerability('python', dep['name'], dep['version'])
                    if vuln:
                        vulnerabilities.append({**dep, **vuln})
            
            # Node.js dependencies
            elif file_name == 'package.json':
                node_deps = self._parse_package_json(file_content)
                dependencies.extend(node_deps)
                
                for dep in node_deps:
                    vuln = self._check_vulnerability('node', dep['name'], dep['version'])
                    if vuln:
                        vulnerabilities.append({**dep, **vuln})
                    
                    # Check for outdated versions
                    latest = self._get_latest_version(dep['name'])
                    if latest and dep['version'] != latest:
                        outdated_packages.append({
                            'name': dep['name'],
                            'current': dep['version'],
                            'latest': latest,
                            'type': dep['type']
                        })
        
        # Remove duplicates
        unique_deps = {f"{d['name']}_{d['type']}": d for d in dependencies}.values()
        
        # Scan for secrets
        secrets = self._scan_for_secrets(repository_data)
        
        # Scan for unsafe imports
        unsafe_imports = self._scan_unsafe_imports(repository_data)
        
        # Calculate security score
        security_score = self._calculate_security_score(vulnerabilities, secrets, unsafe_imports)
        
        return {
            'success': True,
            'dependencies': list(unique_deps),
            'total_dependencies': len(unique_deps),
            'vulnerabilities': vulnerabilities,
            'vulnerability_count': len(vulnerabilities),
            'critical_vulnerabilities': sum(1 for v in vulnerabilities if v.get('severity') == 'critical'),
            'high_vulnerabilities': sum(1 for v in vulnerabilities if v.get('severity') == 'high'),
            'medium_vulnerabilities': sum(1 for v in vulnerabilities if v.get('severity') == 'medium'),
            'low_vulnerabilities': sum(1 for v in vulnerabilities if v.get('severity') == 'low'),
            'outdated_packages': outdated_packages,
            'secrets_found': secrets,
            'unsafe_imports': unsafe_imports,
            'security_score': security_score,
            'recommendations': self._generate_recommendations(vulnerabilities, secrets, outdated_packages)
        }
    
    def _parse_requirements_txt(self, content: str) -> List[Dict]:
        """Parse requirements.txt file"""
        dependencies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Match package name and version
            match = re.match(r'^([a-zA-Z0-9_-]+)(?:[=<>~!]+)([0-9.]+)', line)
            if match:
                dependencies.append({
                    'name': match.group(1),
                    'version': match.group(2),
                    'type': 'python',
                    'file': 'requirements.txt'
                })
            else:
                # Package without version
                pkg_name = line.split('=')[0].split('>')[0].split('<')[0].strip()
                dependencies.append({
                    'name': pkg_name,
                    'version': 'latest',
                    'type': 'python',
                    'file': 'requirements.txt'
                })
        
        return dependencies
    
    def _parse_package_json(self, content: str) -> List[Dict]:
        """Parse package.json file"""
        dependencies = []
        
        try:
            data = json.loads(content)
            
            # Dependencies
            for name, version in data.get('dependencies', {}).items():
                dependencies.append({
                    'name': name,
                    'version': version.replace('^', '').replace('~', ''),
                    'type': 'node',
                    'file': 'package.json',
                    'category': 'production'
                })
            
            # Dev dependencies
            for name, version in data.get('devDependencies', {}).items():
                dependencies.append({
                    'name': name,
                    'version': version.replace('^', '').replace('~', ''),
                    'type': 'node',
                    'file': 'package.json',
                    'category': 'development'
                })
        except:
            pass
        
        return dependencies
    
    def _check_vulnerability(self, ecosystem: str, package: str, version: str) -> Optional[Dict]:
        """Check if package version has known vulnerabilities"""
        vuln_db = self.package_managers.get(ecosystem, {}).get('vulnerability_db', {})
        
        if package in vuln_db:
            for version_range, vuln_info in vuln_db[package].items():
                if self._version_matches(version, version_range):
                    return {
                        'severity': vuln_info['severity'],
                        'cve': vuln_info['cve'],
                        'description': vuln_info['description'],
                        'fix_version': vuln_info['fix_version']
                    }
        
        return None
    
    def _version_matches(self, version: str, version_range: str) -> bool:
        """Check if version matches vulnerability range"""
        # Simplified version comparison
        if version_range.startswith('<'):
            target = float(version_range[1:])
            try:
                current = float(version.split('.')[0] + '.' + version.split('.')[1] if '.' in version else version)
                return current < target
            except:
                return False
        return False
    
    def _get_latest_version(self, package: str) -> Optional[str]:
        """Get latest version of package (mock implementation)"""
        # In production, would query PyPI/npm registry
        latest_versions = {
            'requests': '2.31.0',
            'django': '5.0.0',
            'flask': '3.0.0',
            'express': '4.18.2',
            'lodash': '4.17.21',
            'axios': '1.6.2'
        }
        return latest_versions.get(package)
    
    def _scan_for_secrets(self, repository_data: Dict) -> List[Dict]:
        """Scan for hardcoded secrets in files"""
        secrets = []
        files = repository_data.get('files_preview', [])
        
        for file in files:
            file_name = file.get('name', '')
            file_path = file.get('path', '')
            
            # Skip binary files and large files
            if file.get('size', 0) > 100000:  # 100KB
                continue
            
            # In production, would read actual file content
            # For Phase 10, use mock detection
            mock_content = f"# Content of {file_name}\napi_key = 'sk_test_1234567890abcdef'\npassword = 'secret123'"
            
            for secret_type, pattern in self.secret_patterns.items():
                matches = re.finditer(pattern, mock_content, re.IGNORECASE)
                for match in matches:
                    secrets.append({
                        'type': secret_type,
                        'file': file_path,
                        'line': 1,
                        'severity': 'critical',
                        'suggestion': f'Remove hardcoded {secret_type} and use environment variables'
                    })
                    break  # One per file per type
        
        return secrets[:10]  # Limit results
    
    def _scan_unsafe_imports(self, repository_data: Dict) -> List[Dict]:
        """Scan for unsafe imports/functions"""
        unsafe = []
        files = repository_data.get('files_preview', [])
        
        for file in files:
            file_name = file.get('name', '')
            extension = file.get('extension', '')
            
            if extension == '.py':
                language = 'python'
            elif extension in ['.js', '.jsx', '.ts', '.tsx']:
                language = 'javascript'
            else:
                continue
            
            for unsafe_func in self.unsafe_imports.get(language, []):
                # In production, would parse actual files
                unsafe.append({
                    'function': unsafe_func,
                    'file': file.get('path', file_name),
                    'language': language,
                    'severity': 'high',
                    'suggestion': f'Avoid using {unsafe_func} as it can lead to security vulnerabilities'
                })
                break
        
        return unsafe[:10]
    
    def _calculate_security_score(self, vulnerabilities: List, secrets: List, unsafe_imports: List) -> int:
        """Calculate overall security score (0-100)"""
        score = 100
        
        # Deduct for vulnerabilities
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'medium')
            if severity == 'critical':
                score -= 25
            elif severity == 'high':
                score -= 15
            elif severity == 'medium':
                score -= 8
            else:
                score -= 3
        
        # Deduct for secrets
        score -= len(secrets) * 10
        
        # Deduct for unsafe imports
        score -= len(unsafe_imports) * 5
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, vulnerabilities: List, secrets: List, outdated: List) -> List[Dict]:
        """Generate security recommendations"""
        recommendations = []
        
        if vulnerabilities:
            critical_count = sum(1 for v in vulnerabilities if v.get('severity') == 'critical')
            if critical_count > 0:
                recommendations.append({
                    'priority': 'critical',
                    'title': f'Update {critical_count} critical vulnerability packages',
                    'description': 'Critical vulnerabilities require immediate attention',
                    'action': 'Run package manager update commands to patch vulnerabilities'
                })
            
            recommendations.append({
                'priority': 'high',
                'title': f'Update {len(vulnerabilities)} vulnerable packages',
                'description': 'Vulnerabilities found in dependencies',
                'action': 'Use `pip install --upgrade` or `npm update` to get patched versions'
            })
        
        if secrets:
            recommendations.append({
                'priority': 'critical',
                'title': 'Remove hardcoded secrets',
                'description': f'Found {len(secrets)} hardcoded secrets in code',
                'action': 'Move secrets to environment variables or a secrets manager'
            })
        
        if outdated:
            recommendations.append({
                'priority': 'medium',
                'title': 'Update outdated packages',
                'description': f'{len(outdated)} packages are not on the latest versions',
                'action': 'Review changelogs and update to latest stable versions'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'low',
                'title': 'Dependencies are up to date',
                'description': 'No critical issues found',
                'action': 'Continue regular dependency scans'
            })
        
        return recommendations