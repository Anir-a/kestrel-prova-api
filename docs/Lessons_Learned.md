# Engineering Challenges & Lessons Learned

| Challenge                                 | What Happened                                                                                                                                                              | Resolution                                                                                  | Lesson Learned                                                                      |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Azure AI Foundry Model Access**         | The original Microsoft account and subscription did not have access to the required Azure AI Foundry models. Development could not begin until model access was available. | Migrated to a subscription with supported models and sufficient quota.                      | Validate model availability, quotas and regional support before starting a project. |
| **Azure Capacity & Quotas**               | Several services required quota validation before deployment. Capacity limitations delayed model deployment and testing.                                                   | Reviewed quotas, regions and deployment options before continuing development.              | Capacity planning is as important as architecture planning.                         |
| **Governance Knowledge Base (KB)**        | Early KB ingestion produced inconsistent retrieval quality and weak governance recommendations.                                                                            | Multiple iterations of document structure, chunking, metadata and governance mappings.      | Governance quality depends heavily on KB quality.                                   |
| **Multi-Agent Orchestration**             | Coordinating specialist governance agents proved significantly more complex than expected. Early workflows produced inconsistent outputs.                                  | Redesigned orchestration logic multiple times and simplified agent responsibilities.        | Multi-agent orchestration is harder than building individual agents.                |
| **Structured Governance Outputs**         | Early assessments were verbose, inconsistent and difficult to consume.                                                                                                     | Introduced governance scoring, gates, non-negotiable controls and a standard output schema. | Production AI systems require deterministic and structured outputs.                 |
| **MCP & Approval Logic**                  | Determining appropriate governance approvals and decision points required several design iterations.                                                                       | Introduced governance gates and risk-based approval patterns.                               | Not all agent actions require the same level of governance oversight.               |
| **Azure App Service Deployment**          | Initial deployment and startup behaviour created multiple troubleshooting cycles.                                                                                          | Refined deployment approach, health endpoints and startup configuration.                    | Cloud deployment frequently requires more effort than application development.      |
| **App Service Configuration**             | Missing or incorrect environment variables and application settings prevented successful execution.                                                                        | Validated and documented required App Service settings and environment variables.           | Environment configuration should be treated as part of the solution architecture.   |
| **FastAPI Backend Integration**           | Main.py modifications occasionally introduced startup and deployment failures.                                                                                             | Simplified startup logic and validated dependencies incrementally.                          | Small backend changes can have significant platform impact.                         |
| **Azure AI Foundry Workflow Integration** | Integrating FastAPI with Azure AI Foundry workflows required several redesigns.                                                                                            | Refined workflow invocation, response handling and validation logic.                        | AI workflows should be integrated incrementally and tested independently.           |
| **Multi-Agent Response Handling**         | Foundry workflows returned multiple agent outputs, causing parsing and response issues.                                                                                    | Implemented robust extraction logic and orchestration-level aggregation.                    | Multi-agent systems require specialised response handling.                          |
| **JSON Parsing & Schema Enforcement**     | Early workflow responses occasionally broke frontend expectations.                                                                                                         | Added schema validation, defensive parsing and strict response contracts.                   | Never trust AI output without validation and schema enforcement.                    |
| **Frontend & Governance UX**              | Technical governance findings were difficult for business users to understand.                                                                                             | Redesigned Prova outputs to focus on governance scores, findings and executive summaries.   | Governance tools must be understandable by technical and non-technical audiences.   |
| **Troubleshooting Across Layers**         | Issues frequently appeared across Frontend, API, Foundry and Workflow layers simultaneously.                                                                               | Adopted a layer-by-layer troubleshooting approach.                                          | Isolate and validate one layer at a time.                                           |
| **Observability & Diagnostics**           | Limited visibility increased troubleshooting effort.                                                                                                                       | Added health endpoints, structured logging and diagnostics.                                 | Logging and health checks should exist from day one.                                |

## Key Takeaways

| #  | Lesson                                                                            |
| -- | --------------------------------------------------------------------------------- |
| 1  | Validate Azure AI model availability and quotas before building.                  |
| 2  | Knowledge base quality directly impacts governance quality.                       |
| 3  | Multi-agent orchestration is significantly harder than prompt engineering.        |
| 4  | Structured outputs and schema validation are essential for production AI systems. |
| 5  | Never trust raw AI output without validation.                                     |
| 6  | Document App Service settings and environment variables early.                    |
| 7  | Build health endpoints and logging before troubleshooting begins.                 |
| 8  | Test Frontend, API, Foundry and Workflow layers independently.                    |
| 9  | Governance systems must be explainable, auditable and repeatable.                 |
| 10 | Building an AI agent is easy; building a governed AI platform is much harder.     |

### Final Outcome

✅ Azure AI Foundry Agent Service

✅ Kestrel Multi-Agent Governance Engine

✅ Prova AI Governance Inspector

✅ FastAPI Backend

✅ GitHub Pages Frontend

✅ Structured Governance Scoring Framework

✅ Australian AI Governance Alignment

✅ End-to-End Working Solution Submitted to Microsoft Agent League 2026
