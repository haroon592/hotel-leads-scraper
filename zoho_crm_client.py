import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ZohoCRMClient:
    def __init__(self):
        self.client_id = os.getenv('ZOHO_CLIENT_ID')
        self.client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        self.refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
        self.redirect_uri = os.getenv('ZOHO_REDIRECT_URI', 'http://localhost:8000/callback')
        self.access_token = None
        self.token_expiry = 0
        
        # Zoho API endpoints
        self.token_url = "https://accounts.zoho.com/oauth/v2/token"
        self.api_base_url = "https://www.zohoapis.com/crm/v2"
        
    def get_access_token(self):
        """Get or refresh access token"""
        current_time = time.time()
        
        # If token is still valid, return it
        if self.access_token and current_time < self.token_expiry:
            return self.access_token
        
        # Request new access token
        params = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(self.token_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data['access_token']
            # Set expiry to 5 minutes before actual expiry
            self.token_expiry = current_time + data.get('expires_in', 3600) - 300
            
            return self.access_token
            
        except Exception as e:
            print(f"✗ Error getting Zoho access token: {e}")
            raise
    
    def get_headers(self):
        """Get headers with authentication"""
        token = self.get_access_token()
        return {
            'Authorization': f'Zoho-oauthtoken {token}',
            'Content-Type': 'application/json'
        }
    
    def parse_csv_lead(self, csv_file_path):
        """Parse CSV file and extract lead data"""
        try:
            import csv
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                leads = list(reader)
                
                # Filter out empty rows (where all values are empty/None)
                leads = [lead for lead in leads if any(v and str(v).strip() for v in lead.values())]
                
                return leads
        except Exception as e:
            print(f"  ✗ Error parsing CSV {csv_file_path}: {e}")
            return []
    
    def upload_lead(self, lead_data):
        """Upload a single lead to Zoho CRM"""
        try:
            # Map CSV fields to Zoho CRM fields
            # Adjust these field mappings based on your CSV structure and Zoho CRM fields
            crm_lead = {
                "Company": lead_data.get("Company", lead_data.get("Property_Name", "Unknown")),
                "Last_Name": lead_data.get("Contact_Name", "Lead"),
                "Email": lead_data.get("Email", ""),
                "Phone": lead_data.get("Phone", ""),
                "City": lead_data.get("City", ""),
                "State": lead_data.get("State", ""),
                "Country": lead_data.get("Country", ""),
                "Description": lead_data.get("Description", ""),
                "Lead_Source": "Hotel Project Leads",
                "Lead_Status": "Not Contacted",
            }
            
            # Add custom fields if available
            if lead_data.get("Project_Type"):
                crm_lead["Project_Type"] = lead_data["Project_Type"]
            if lead_data.get("Project_Stage"):
                crm_lead["Project_Stage"] = lead_data["Project_Stage"]
            if lead_data.get("Estimated_Budget"):
                crm_lead["Estimated_Budget"] = lead_data["Estimated_Budget"]
            
            # Remove empty fields
            crm_lead = {k: v for k, v in crm_lead.items() if v}
            
            # Make API request
            url = f"{self.api_base_url}/Leads"
            payload = {"data": [crm_lead]}
            
            response = requests.post(url, headers=self.get_headers(), json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get('data') and result['data'][0].get('status') == 'success':
                return True, result['data'][0].get('details', {}).get('id')
            else:
                return False, result.get('data', [{}])[0].get('message', 'Unknown error')
                
        except Exception as e:
            return False, str(e)
    
    def upload_leads_from_directory(self, download_dir):
        """Upload all CSV files from the download directory"""
        success_count = 0
        failed_count = 0
        skipped_count = 0
        uploaded_leads = []
        
        # Get all CSV files (excluding log files)
        csv_files = [f for f in os.listdir(download_dir) 
                     if f.endswith('.csv') and not f.startswith('zoho_upload_log')]
        total_files = len(csv_files)
        
        if total_files == 0:
            print("No CSV files found to upload")
            return success_count, failed_count, uploaded_leads
        
        print(f"Uploading {total_files} leads to Zoho CRM...")
        
        for idx, csv_file in enumerate(csv_files, 1):
            csv_path = os.path.join(download_dir, csv_file)
            
            # Progress indicator every 100 files
            if idx % 100 == 0:
                print(f"Progress: {idx}/{total_files} ({(idx/total_files)*100:.0f}%)")
            
            leads = self.parse_csv_lead(csv_path)
            
            if not leads:
                skipped_count += 1
                continue
            
            # Process each lead in the CSV
            for lead_data in leads:
                success, result = self.upload_lead(lead_data)
                
                if success:
                    success_count += 1
                    uploaded_leads.append({
                        'file': csv_file,
                        'company': lead_data.get("Company", lead_data.get("Property_Name", "Unknown")),
                        'zoho_id': result
                    })
                else:
                    failed_count += 1
                
                # Rate limiting - Zoho has API limits (100 calls per minute)
                time.sleep(0.6)
        
        print(f"Upload complete: {success_count} success, {failed_count} failed, {skipped_count} skipped")
        
        # Save upload log
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'total_files': total_files,
            'success_count': success_count,
            'failed_count': failed_count,
            'uploaded_leads': uploaded_leads
        }
        
        log_file = os.path.join(download_dir, f"zoho_upload_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return success_count, failed_count, uploaded_leads


def generate_zoho_tokens():
    """
    Helper function to generate initial Zoho tokens.
    This needs to be run once to get the refresh token.
    """
    print("="*60)
    print("ZOHO CRM TOKEN GENERATION")
    print("="*60)
    print("\nStep 1: Go to Zoho API Console: https://api-console.zoho.com/")
    print("Step 2: Create a Server-based Application")
    print("Step 3: Note down Client ID and Client Secret")
    print("Step 4: Set Redirect URI as: http://localhost:8000/callback")
    print("Step 5: Generate authorization code with this URL:\n")
    
    client_id = input("Enter your Client ID: ").strip()
    scope = "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL"
    redirect_uri = "http://localhost:8000/callback"
    
    auth_url = f"https://accounts.zoho.com/oauth/v2/auth?scope={scope}&client_id={client_id}&response_type=code&access_type=offline&redirect_uri={redirect_uri}"
    
    print(f"\nOpen this URL in your browser:\n{auth_url}\n")
    print("After authorization, you'll be redirected to a URL like:")
    print("http://localhost:8000/callback?code=AUTHORIZATION_CODE\n")
    
    auth_code = input("Paste the authorization code from the URL: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    
    # Exchange authorization code for tokens
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("\n" + "="*60)
        print("SUCCESS! Save these to your .env file:")
        print("="*60)
        print(f"\nZOHO_CLIENT_ID={client_id}")
        print(f"ZOHO_CLIENT_SECRET={client_secret}")
        print(f"ZOHO_REFRESH_TOKEN={data['refresh_token']}")
        print(f"ZOHO_REDIRECT_URI={redirect_uri}")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")


if __name__ == '__main__':
    # Run token generation if executed directly
    generate_zoho_tokens()
