# NASA APOD MLOps Pipeline

An automated data pipeline using Apache Airflow to fetch NASA's Astronomy Picture of the Day (APOD), with MLOps practices including data versioning with DVC.

## 🚀 Features

- **Data Extraction**: Fetches NASA APOD data daily via API
- **Data Storage**: 
  - Images saved to local storage
  - Metadata stored in PostgreSQL database
  - CSV export for data versioning
- **Data Versioning**: DVC tracks changes to dataset
- **Orchestration**: Airflow DAG with task dependencies
- **Code Versioning**: Git/GitHub for pipeline code

## 📁 Project Structure

```
MLops3/
├── dags/
│   └── nasa_apod_dag.py          # Main Airflow DAG
├── include/
│   ├── apod_data.csv              # NASA APOD metadata
│   ├── apod_data.csv.dvc          # DVC tracking file
│   ├── .dvc/                      # DVC configuration
│   └── images/                    # Downloaded images
├── tests/
│   └── dags/
│       └── test_dag_example.py    # DAG validation tests
├── Dockerfile                     # Container definition
├── requirements.txt               # Python dependencies
├── docker-compose.override.yml    # Docker compose overrides
└── .env                          # Environment variables
```

## 🛠️ Setup & Installation

### Prerequisites
- Docker Desktop
- Astro CLI (`winget install -e --id Astronomer.Astro`)
- Git

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/Abdul-Hanan-Choudhry/MLOPS_A3.git
cd MLOPS_A3
```

2. **Start Airflow**
```bash
astro dev start
```

3. **Access Airflow UI**
- URL: `http://localhost:8081`
- Username: `admin`
- Password: `admin`

## 🔧 Configuration

### Environment Variables (.env)
```env
nasa_api_key=YOUR_NASA_API_KEY
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
```

### Database
- **Host**: postgres (internal) / localhost:5433 (external)
- **Database**: airflow
- **Table**: apod_data

## 📊 DAG Details

**DAG ID**: `nasa_apod_pipeline`

**Schedule**: Daily (`@daily`)

**Tasks**:
1. `fetch_nasa_apod` - Fetches data from NASA API, saves image and CSV
2. `version_with_dvc` - Tracks CSV changes with DVC

**Tags**: `["nasa", "etl", "mlops"]`

**Retries**: 2

## 🗂️ Data Versioning with DVC

The project uses DVC to version the APOD dataset:

```bash
# Pull latest data
dvc pull

# Check data status
dvc status

# View data changes
git log include/apod_data.csv.dvc
```

## 🧪 Testing

Run DAG validation tests:
```bash
astro dev pytest
```

Tests verify:
- No import errors
- Required tags present
- Retry configuration

## 📦 Dependencies

- **requests**: HTTP API calls
- **pandas**: Data manipulation
- **psycopg2-binary**: PostgreSQL connectivity
- **dvc**: Data version control
- **python-dotenv**: Environment variable management

## 🎯 Pipeline Flow

```
NASA API → Fetch Data → Save Image → Save CSV → Save to Postgres → DVC Versioning
```

## 📸 Sample Output

The pipeline generates:
- **Images**: `/include/images/[title].jpg`
- **CSV**: `/include/apod_data.csv`
- **Database**: `apod_data` table in Postgres

## 🤝 Contributing

This is an academic project for MLOps coursework.

## 📄 License

Educational use only.

## 👤 Author

Abdul Hanan Choudhry

## 🔗 Links

- **GitHub Repository**: https://github.com/Abdul-Hanan-Choudhry/MLOPS_A3.git
- **NASA APOD API**: https://api.nasa.gov/
```