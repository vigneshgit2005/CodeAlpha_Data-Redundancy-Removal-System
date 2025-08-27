# redundancy_system_simple.py
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    """Data validation using content hashing"""
    
    def generate_hash(self, data: Dict) -> str:
        """Generate hash from data dictionary"""
        # Create a normalized version for consistent hashing
        normalized_data = {k: str(v).lower().strip() for k, v in data.items() if k != 'timestamp'}
        data_str = json.dumps(normalized_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def is_duplicate(self, new_data: Dict, existing_data: Dict) -> bool:
        """Check if data is duplicate using hashing"""
        new_hash = self.generate_hash(new_data)
        existing_hash = self.generate_hash(existing_data)
        return new_hash == existing_hash

class RedundancyDetector:
    """Main class for redundancy detection"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.processed_count = 0
        self.duplicate_count = 0
        self.unique_count = 0
    
    def check_redundancy(self, new_data: Dict, existing_data_list: List[Dict]) -> Tuple[bool, Optional[Dict]]:
        """
        Check if new data is redundant against existing data
        
        Returns:
            Tuple[bool, Optional[Dict]]: (is_duplicate, matching_entry)
        """
        self.processed_count += 1
        
        for existing_data in existing_data_list:
            if self.validator.is_duplicate(new_data, existing_data):
                self.duplicate_count += 1
                return True, existing_data
        
        self.unique_count += 1
        return False, None

class CloudDatabaseSimulator:
    """Simulates a cloud database for demonstration"""
    
    def __init__(self):
        self.data_store = []
        self.detector = RedundancyDetector()
    
    def add_data(self, new_data: Dict) -> Dict:
        """Add new data after redundancy check"""
        
        # Add timestamp for tracking
        new_data['timestamp'] = datetime.now().isoformat()
        
        # Check for redundancy
        is_duplicate, existing_entry = self.detector.check_redundancy(new_data, self.data_store)
        
        if is_duplicate:
            return {
                'status': 'rejected',
                'reason': 'duplicate_found',
                'existing_data': existing_entry,
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Add unique ID and store
            new_data['unique_id'] = str(uuid.uuid4())
            self.data_store.append(new_data.copy())
            
            return {
                'status': 'added',
                'id': new_data['unique_id'],
                'timestamp': datetime.now().isoformat()
            }
    
    def get_all_data(self) -> List[Dict]:
        """Get all stored data"""
        return self.data_store.copy()
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        return {
            'total_processed': self.detector.processed_count,
            'duplicates_found': self.detector.duplicate_count,
            'unique_entries': self.detector.unique_count,
            'total_stored': len(self.data_store)
        }

def main():
    """Main function to demonstrate the system"""
    print("=== Data Redundancy Removal System ===\n")
    
    # Initialize the database simulator
    db = CloudDatabaseSimulator()
    
    # Sample test data
    test_data = [
        {'name': 'John Doe', 'email': 'john@example.com', 'age': 30, 'city': 'New York'},
        {'name': 'John Doe', 'email': 'john@example.com', 'age': 30, 'city': 'New York'},  # Exact duplicate
        {'name': 'john doe', 'email': 'JOHN@example.com', 'age': 30, 'city': 'New York'},  # Different case
        {'name': 'Jane Smith', 'email': 'jane@example.com', 'age': 25, 'city': 'London'},  # Unique
        {'name': 'John Doe', 'email': 'john@example.com', 'age': 30, 'city': 'Boston'},    # Different city
        {'name': 'Jane Smith', 'email': 'jane@example.com', 'age': 25, 'city': 'London'},  # Duplicate of Jane
    ]
    
    print("Processing test data...\n")
    
    # Process each data entry
    for i, data in enumerate(test_data, 1):
        result = db.add_data(data)
        
        print(f"Entry {i}: {data['name']} - {result['status'].upper()}")
        if result['status'] == 'rejected':
            print(f"   Reason: {result['reason']}")
            print(f"   Existing: {result['existing_data']['name']} (ID: {result['existing_data']['unique_id']})")
        print()
    
    # Display results
    print("\n=== Final Results ===")
    stats = db.get_stats()
    print(f"Total processed: {stats['total_processed']}")
    print(f"Duplicates found: {stats['duplicates_found']}")
    print(f"Unique entries added: {stats['unique_entries']}")
    print(f"Total stored in DB: {stats['total_stored']}")
    
    print("\n=== Stored Data ===")
    for i, entry in enumerate(db.get_all_data(), 1):
        print(f"{i}. {entry['name']} - {entry['email']} - {entry['city']} (ID: {entry['unique_id'][:8]}...)")

if __name__ == "__main__":
    main()