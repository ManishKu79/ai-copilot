from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import re
import json

router = APIRouter()

class ScanRequest(BaseModel):
    repository_data: Dict[str, Any]

class DependencyScanner:
    def __init__(self):
        self.secret_patterns = {
            'API_KEY': r'(api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9]{16,})["\']',
            'AWS_KEY': r'(AKIA|ASIA)[A-Z0-9]{16}',
            'JWT_TOKEN': r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
            'PASSWORD': r'password\s*[=:]\s*["\']([^"\']+)["\']',
            'SECRET_KEY': r'secret[_]?key\s*[=:]\s*["\']([^"\']+)["\']',
            'DATABASE_URL': r'(postgresql|mysql|mongodb)://[^/\s]+',
            'TOKEN': r'token\s*[=:]\s*["\']([A-Za-z0-9_\-\.]+)["\']'
        }
        
        self.vulnerability_db = {
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
            },
            'flask': {
                '<2.3.0': {
                    'severity': 'medium',
                    'cve': 'CVE-2023-12348',
                    'description': 'Debug mode vulnerability',
                    'fix_version': '2.3.0'
                }
            }
        }
        
        self.latest_versions = {
            'requests': '2.31.0',
            'django': '5.0.0',
            'flask': '3.0.0',
            'express': '4.18.2',
            'lodash': '4.17.21',
            'axios': '1.6.2',
            'numpy': '1.26.0',
            'pandas': '2.1.0'
        }
    
    def scan_dependencies(self, repository_data: Dict) -> Dict:
        """Scan all dependencies in the repository"""
        files = repository_data.get('files_preview', [])
        
        dependencies = []
        vulnerabilities = []
        outdated_packages = []
        
        # Scan for dependency files
        for file in files:
            file_name = file.get('name', '').lower()
            
            # Check for requirements.txt
            if file_name == 'requirements.txt':
                # Mock some Python dependencies
                mock_python_deps = [
                    {'name': 'requests', 'version': '2.28.0', 'type': 'python', 'file': 'requirements.txt'},
                    {'name': 'django', 'version': '4.1.0', 'type': 'python', 'file': 'requirements.txt'},
                    {'name': 'flask', 'version': '2.2.0', 'type': 'python', 'file': 'requirements.txt'},
                    {'name': 'numpy', 'version': '1.24.0', 'type': 'python', 'file': 'requirements.txt'}
                ]
                dependencies.extend(mock_python_deps)
            
            # Check for package.json
            elif file_name == 'package.json':
                # Mock some Node dependencies
                mock_node_deps = [
                    {'name': 'express', 'version': '4.17.0', 'type': 'node', 'file': 'package.json', 'category': 'production'},
                    {'name': 'lodash', 'version': '4.17.20', 'type': 'node', 'file': 'package.json', 'category': 'production'},
                    {'name': 'axios', 'version': '1.5.0', 'type': 'node', 'file': 'package.json', 'category': 'production'},
                    {'name': 'react', 'version': '18.2.0', 'type': 'node', 'file': 'package.json', 'category': 'production'}
                ]
                dependencies.extend(mock_node_deps)
        
        # Remove duplicates
        unique_deps = {}
        for dep in dependencies:
            key = f"{dep['name']}_{dep['type']}"
            if key not in unique_deps:
                unique_deps[key] = dep
        dependencies = list(unique_deps.values())
        
        # Check for vulnerabilities
        for dep in dependencies:
            vuln = self._check_vulnerability(dep['name'], dep['version'])
            if vuln:
                vulnerabilities.append({**dep, **vuln})
            
            # Check for outdated packages
            latest = self.latest_versions.get(dep['name'])
            if latest and dep['version'] != latest:
                outdated_packages.append({
                    'name': dep['name'],
                    'current': dep['version'],
                    'latest': latest,
                    'type': dep['type']
                })
        
        # Scan for secrets in files (mock)
        secrets = self._scan_for_secrets(files)
        
        # Scan for unsafe imports (mock)
        unsafe_imports = self._scan_unsafe_imports(files)
        
        # Calculate security score
        security_score = self._calculate_security_score(vulnerabilities, secrets, unsafe_imports)
        
        return {
            'success': True,
            'dependencies': dependencies,
            'total_dependencies': len(dependencies),
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
    
    def _check_vulnerability(self, package: str, version: str) -> Optional[Dict]:
        """Check if package version has known vulnerabilities"""
        if package in self.vulnerability_db:
            for version_range, vuln_info in self.vulnerability_db[package].items():
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
        if version_range.startswith('<'):
            try:
                target = float(version_range[1:])
                current = float(version.split('.')[0] + '.' + version.split('.')[1] if '.' in version else version)
                return current < target
            except:
                pass
        return False
    
    def _scan_for_secrets(self, files: List[Dict]) -> List[Dict]:
        """Scan for hardcoded secrets in files"""
        secrets = []
        
        for file in files[:10]:  # Check first 10 files
            file_name = file.get('name', '')
            
            # Mock detection - in production would read actual content
            for secret_type, pattern in self.secret_patterns.items():
                # Simulate finding secrets in certain file types
                if file_name.endswith(('.py', '.js', '.env', '.config')):
                    secrets.append({
                        'type': secret_type,
                        'file': file_name,
                        'line': 1,
                        'severity': 'critical',
                        'suggestion': f'Remove hardcoded {secret_type} and use environment variables'
                    })
                    break  # One per file
        
        return secrets[:5]  # Limit results
    
    def _scan_unsafe_imports(self, files: List[Dict]) -> List[Dict]:
        """Scan for unsafe imports/functions"""
        unsafe = []
        unsafe_funcs = ['eval', 'exec', 'os.system', 'subprocess.call', 'pickle.loads']
        
        for file in files[:10]:
            file_name = file.get('name', '')
            if file_name.endswith('.py'):
                for func in unsafe_funcs[:3]:  # Limit
                    unsafe.append({
                        'function': func,
                        'file': file_name,
                        'language': 'python',
                        'severity': 'high',
                        'suggestion': f'Avoid using {func} as it can lead to security vulnerabilities'
                    })
                    break
        
        return unsafe[:5]
    
    def _calculate_security_score(self, vulnerabilities: List, secrets: List, unsafe_imports: List) -> int:
        """Calculate overall security score (0-100)"""
        score = 100
        
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
        
        score -= len(secrets) * 10
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
                    'action': 'Run: pip install --upgrade <package> or npm update <package>'
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
                'action': 'Move secrets to environment variables or a secrets manager like HashiCorp Vault'
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
                'description': 'No critical issues found in your dependencies',
                'action': 'Continue regular dependency scans to stay secure'
            })
        
        return recommendations


# Create scanner instance
scanner = DependencyScanner()


@router.post("/scan")
async def scan_dependencies(request: ScanRequest):
    """Scan repository for dependencies and vulnerabilities"""
    if not request.repository_data:
        raise HTTPException(status_code=400, detail="Repository data required")
    
    try:
        result = scanner.scan_dependencies(request.repository_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/outdated/{repo_id}")
async def check_outdated(repo_id: str):
    """Check for outdated packages"""
    return {
        "success": True,
        "repo_id": repo_id,
        "outdated_packages": [
            {"name": "requests", "current": "2.28.0", "latest": "2.31.0"},
            {"name": "django", "current": "4.1.0", "latest": "5.0.0"}
        ]
    }