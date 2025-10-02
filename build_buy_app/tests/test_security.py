"""
Security Test Suite for Build vs Buy Dashboard
Test security measures to ensure they block malicious inputs while preserving functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_security_integration():
    """Test that security configuration doesn't break the app."""
    from app import BuildVsBuyApp
    
    app = BuildVsBuyApp()
    
    # Verify app created successfully
    assert app.app is not None
    assert len(app.app.callback_map) == 19  # All callbacks still registered
    
    print("✅ Security integration test passed")


def test_input_validation():
    """Test input validation and sanitization."""
    from config.security import security_config
    
    # Test normal inputs
    assert security_config.secure_float_conversion("123.45") == 123.45
    assert security_config.secure_float_conversion("0") == 0.0
    assert security_config.secure_float_conversion("") == 0.0
    assert security_config.secure_float_conversion(None) == 0.0
    
    # Test malicious inputs
    assert security_config.secure_float_conversion("<script>alert('xss')</script>") == 0.0
    assert security_config.secure_float_conversion("javascript:void(0)") == 0.0
    assert security_config.secure_float_conversion("eval(malicious_code)") == 0.0
    
    print("✅ Input validation test passed")


def test_string_sanitization():
    """Test string input sanitization."""
    from config.security import security_config
    
    # Test normal strings
    normal_input = "Normal text input"
    assert security_config.validate_inputs(normal_input) == normal_input
    
    # Test malicious strings (should raise ValueError)
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "javascript:void(0)",
        "eval(malicious_code)",
        "onload=malicious()",
        "__import__('os').system('rm -rf /')"
    ]
    
    for malicious in malicious_inputs:
        try:
            security_config.validate_inputs(malicious)
            assert False, f"Should have blocked malicious input: {malicious}"
        except ValueError:
            pass  # Expected behavior
    
    print("✅ String sanitization test passed")


def test_production_detection():
    """Test production environment detection."""
    from config.security import security_config
    
    # In development (no PORT env var)
    assert not security_config.is_production
    
    # Simulate production
    os.environ['PORT'] = '8080'
    from config.security import DashSecurityConfig
    prod_config = DashSecurityConfig()
    assert prod_config.is_production
    
    # Clean up
    del os.environ['PORT']
    
    print("✅ Production detection test passed")


def test_safe_float_function():
    """Test the updated safe_float function."""
    from app import safe_float
    
    # Normal inputs
    assert safe_float("123.45") == 123.45
    assert safe_float("0") == 0.0
    assert safe_float(None) == 0.0
    assert safe_float("") == 0.0
    
    # Should handle malicious inputs gracefully
    assert safe_float("<script>") == 0.0
    assert safe_float("javascript:") == 0.0
    
    print("✅ Safe float function test passed")


def test_app_with_malicious_inputs():
    """Test that the app handles malicious inputs in a realistic scenario."""
    from app import BuildVsBuyApp
    
    app = BuildVsBuyApp()
    
    # Test parameters with malicious content
    malicious_params = {
        'build_timeline': "<script>alert('xss')</script>",
        'fte_cost': "javascript:void(0)",
        'fte_count': "eval(malicious)",
        'useful_life': "onload=attack()",
        'prob_success': "__import__('os')",
        'wacc': "normal_value_8"
    }
    
    # Process through safe_float
    from app import safe_float
    for key, value in malicious_params.items():
        safe_value = safe_float(value)
        assert isinstance(safe_value, float)
        # Malicious strings should become 0.0, valid numbers should convert
        if key == 'wacc':
            assert safe_value == 0.0  # "normal_value_8" is not a valid number
        else:
            assert safe_value == 0.0  # All malicious inputs become 0.0
    
    print("✅ App malicious input handling test passed")


if __name__ == "__main__":
    print("🛡️ Running Security Test Suite...")
    print("=" * 50)
    
    try:
        test_security_integration()
        test_input_validation()
        test_string_sanitization()
        test_production_detection()
        test_safe_float_function()
        test_app_with_malicious_inputs()
        
        print("=" * 50)
        print("🎉 ALL SECURITY TESTS PASSED!")
        print("✅ App is secure and functional")
        print("🛡️ Ready for production deployment")
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        print("=" * 50)
        print("🔧 Please fix security issues before deployment.")
        raise
