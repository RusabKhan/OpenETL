![OpenETL Logo](https://cdn.dataomnisolutions.com/main/logos/open-etl.png)

_By [DataOmni Solutions](https://dataomnisolutions.com)_

![dashboard_new](https://cdn.dataomnisolutions.com/main/app/dashboard.png?v=1)

OpenETL is a robust and scalable ETL (Extract, Transform, Load) application built with modern technologies like
**FastAPI**, **Next.js**, and **Apache Spark**. The application offers an intuitive, user-friendly interface that
simplifies the ETL process, empowering users to effortlessly extract data from various sources, apply transformations,
and load it into your desired target destinations.

### Key Features of OpenETL:

- **Backend**: Powered by **Python 3.12** and **FastAPI**, ensuring fast and efficient data processing and API
  interactions.
- **Frontend**: Built with **Next.js**, providing a smooth and interactive user experience.
- **Compute Engine**: **Apache Spark** is integrated for distributed data processing, enabling scalable and
  high-performance operations.
- **Task Execution**: Utilizes **Celery** to handle background task processing, ensuring reliable execution of
  long-running operations.
- **Scheduling**: **APScheduler** is used to manage and schedule ETL jobs, allowing for automated workflows.

## Features

- **ETL with Full Load**: Easily extract data from different sources and load it into your preferred target location.
- **Scheduled Timing**: Schedule your ETL tasks to run at specific intervals, ensuring your data is always up-to-date.
- **User Interface**: A clean and user-friendly UI to monitor and control your ETL processes with ease.
- **Logging**: Comprehensive logging to track every action, error, and data transformation throughout the ETL pipeline.
- **Integration History**: Keep track of all your integration jobs with detailed records of past runs, including
  statuses and errors.
- **Batch Processing**: Handle large volumes of data by processing it in batches for better efficiency.
- **Distributed Spark Computing**: Utilize Spark for distributed computing, allowing you to process large datasets
  efficiently across multiple nodes.

## Benchmark

Check the detailed performance benchmark of OpenETL [here](https://cdn.dataomnisolutions.com/main/app/benchmark.html).

---

## Getting Started

To get started with OpenETL, follow these steps:

## Environment Variables

OpenETL relies on a `.env` file for configuration. Ensure the following variables are defined in your local `.env` file,
and **update them** according to your environment:

```bash
OPENETL_DOCUMENT_HOST=postgres
OPENETL_DOCUMENT_DB=openetl_db
OPENETL_DOCUMENT_SCHEMA=public
OPENETL_DOCUMENT_USER=openetl
OPENETL_DOCUMENT_PASS=openetl123
OPENETL_DOCUMENT_PORT=5432
OPENETL_DOCUMENT_ENGINE=PostgreSQL
OPENETL_HOME=/app
CELERY_BROKER_URL=redis://redis:6379/0
SPARK_MASTER=spark://spark-master:7077
SPARK_DRIVER_HOST=openetl-celery-worker-1
```

### Using Docker

1. Ensure that you have Docker installed on your local machine.
2. Clone this repository to your local environment.
3. Open a terminal or command prompt and navigate to the project directory.
4. Build the `backend` image by running the following command:
   4.1
    ```sh
    docker compose up --build -d backend
    ```
5. Launch the Docker container:
    ```sh
    docker compose up --build -d
    ```
6. Open your web browser and visit `http://localhost:3001` to access the OpenETL application.

After running successfully, the API documentation can be found
at [http://localhost:5009/docs](http://localhost:5009/docs), and the UI can be accessed
at [http://localhost:3001](http://localhost:3001).

## Need More?

OpenETL is a free application that offers a range of powerful features. However, if you're looking for advanced
capabilities, we also offer Pro and an Enterprise version with additional features and customizations.

### Features Comparison
| Feature                                    |  Basic Version  |   Pro Version         | Enterprise Version       |
|--------------------------------------------|:---------------:|:---------------------:|:------------------------:|
| Free Full Load ETL                         | ✅ Available     | ✅ Available           | ✅ Available              |
| Scheduled Timing                           | ✅ Available     | ✅ Available           | ✅ Available              |
| User Interface (UI)                        | ✅ Available     | ✅ Available           | ✅ Available              |
| Logging                                    | ✅ Available     | ✅ Available           | ✅ Available              |
| Integration History                        | ✅ Available     | ✅ Available           | ✅ Available              |
| Batches                                    | ✅ Available     | ✅ Available           | ✅ Available              |
| Distributed Spark Computing (Configurable) | ✅ Available     | ✅ Available           | ✅ Available              |
| NaN Value Replacement Based on Data Type   | ✅ Available     | ✅ Available           | ✅ Available              |
| Views (ID mapping and data attachment)     | ❌ Not Available | ✅ Available           | ✅ Available              |
| Support                                    | ❌ Not Available | ✅ Available           | ✅ Available              |
| Dedicated Machine for Running the App      | ❌ Not Available | ✅ Available           | ✅ Available              |
| Custom Schema Declarations                 | ❌ Not Available | ✅ Available           | ✅ Available              |
| Python-Based Transformations               | ❌ Not Available | ✅ Available           | ✅ Available              |
| Permission-Based Users                     | ❌ Not Available | ✅ Available           | ✅ Available              |
| Dtype Casting                              | ❌ Not Available | ✅ Available           | ✅ Available              |
| Custom Development                         | ❌ Not Available | ❌ Not Available       | ✅ Available              |


If the features in the base version of OpenETL aren't quite cutting it for you, fear not! We're here to help. If you
require additional functionality, customizations, or have specific requirements, reach out to us.

For more information, visit [dataomnisolutions.com](https://www.dataomnisolutions.com) or contact us
at [sales@dataomnisolutions.com](mailto:sales@dataomnisolutions.com).

## Support and Feedback

If you encounter any issues or have suggestions for improving OpenETL, please don't hesitate to open an issue in the
GitHub repository. We greatly appreciate your feedback and are dedicated to enhancing the application based on user
input. You can read the proper way to report issues in the [Security Section](SECURITY.md).

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

Thank you for choosing OpenETL! We hope it simplifies your ETL tasks and provides a seamless experience.
