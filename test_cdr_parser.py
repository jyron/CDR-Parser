import unittest
from cdr_parser import parse_cdr_line, parse_basic, parse_extended, parse_hex


class TestCDRParser(unittest.TestCase):
    """Simple tests for CDR parser functionality"""

    def test_basic_format(self):
        """Test basic format: <id>,<bytes_used>"""
        line = "9991,2935"
        result = parse_cdr_line(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 9991)
        self.assertEqual(result["bytes_used"], 2935)
        self.assertIsNone(result["mnc"])
        self.assertIsNone(result["dmcc"])
        self.assertIsNone(result["cellid"])
        self.assertIsNone(result["ip"])

    def test_extended_format(self):
        """Test extended format: <id>,<dmcc>,<mnc>,<bytes_used>,<cellid>"""
        line = "4,0d39f,0,495594,214"
        result = parse_cdr_line(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 4)
        self.assertEqual(result["mnc"], 0)
        self.assertEqual(result["bytes_used"], 495594)
        self.assertEqual(result["dmcc"], "0d39f")
        self.assertEqual(result["cellid"], 214)
        self.assertIsNone(result["ip"])

    def test_hex_format(self):
        """Test hex format: <id>,<hex_string>"""
        line = "16,be833279000000c063e5e63d"
        result = parse_cdr_line(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 16)
        self.assertEqual(result["mnc"], 48771)  # be83 in hex
        self.assertEqual(result["bytes_used"], 12921)  # 3279 in hex
        self.assertEqual(result["cellid"], 192)  # 000000c0 in hex
        self.assertEqual(result["ip"], "99.229.230.61")  # 63.e5.e6.3d in hex
        self.assertIsNone(result["dmcc"])

    def test_empty_line(self):
        """Test that empty lines return None"""
        result = parse_cdr_line("")
        self.assertIsNone(result)
        
        result = parse_cdr_line("   ")
        self.assertIsNone(result)

    def test_invalid_format_single_value(self):
        """Test that lines with single value return None"""
        result = parse_cdr_line("12345")
        self.assertIsNone(result)

    def test_invalid_format_no_comma(self):
        """Test that lines without commas return None"""
        result = parse_cdr_line("not a valid line")
        self.assertIsNone(result)

    def test_multiple_basic_records(self):
        """Test multiple basic format records"""
        test_cases = [
            ("1,1000", {"id": 1, "bytes_used": 1000}),
            ("12,5000", {"id": 12, "bytes_used": 5000}),
            ("9999,12345", {"id": 9999, "bytes_used": 12345}),
        ]
        
        for line, expected in test_cases:
            result = parse_cdr_line(line)
            self.assertEqual(result["id"], expected["id"])
            self.assertEqual(result["bytes_used"], expected["bytes_used"])

    def test_multiple_extended_records(self):
        """Test multiple extended format records"""
        test_cases = [
            ("14,abc123,100,50000,999", {"id": 14, "dmcc": "abc123", "mnc": 100, "bytes_used": 50000, "cellid": 999}),
            ("24,xyz789,200,75000,888", {"id": 24, "dmcc": "xyz789", "mnc": 200, "bytes_used": 75000, "cellid": 888}),
        ]
        
        for line, expected in test_cases:
            result = parse_cdr_line(line)
            self.assertEqual(result["id"], expected["id"])
            self.assertEqual(result["dmcc"], expected["dmcc"])
            self.assertEqual(result["mnc"], expected["mnc"])
            self.assertEqual(result["bytes_used"], expected["bytes_used"])
            self.assertEqual(result["cellid"], expected["cellid"])

    def test_format_detection_by_id(self):
        """Test that format is correctly detected based on last digit of ID"""
        # ID ending in 4 -> extended format
        result = parse_cdr_line("4,dmcc,10,1000,50")
        self.assertEqual(result["dmcc"], "dmcc")
        
        # ID ending in 6 -> hex format
        result = parse_cdr_line("6,be833279000000c063e5e63d")
        self.assertIsNotNone(result["ip"])
        
        # Other IDs -> basic format
        result = parse_cdr_line("5,1000")
        self.assertEqual(result["bytes_used"], 1000)
        self.assertIsNone(result["dmcc"])


if __name__ == "__main__":
    unittest.main()

