## Diagram For Backend Architecture of SociaLink
<!-- Use flowchart TD  instead of graph LR for different layout-->
``` mermaid
graph LR
  A{{User}} -->|Client Request| B((Middleware Processing));
  B --> C{URL Routing};
  C --> D[/User Autentication/];
  C --> E[/Profile Managemnet/];
  C --> F[/Oauth Integration/];
  C --> G[/Content Management/];
  D --> H{URL Routing};
  E --> H;
  F --> H;
  G --> H;
  H --> I@{ shape: procs, label: "View Function Execution"};
  I --> J[Model Interaction];
  J --> I;
  I --> K[Template Rendering];
  K --> I;
  I --> L[Forms Handling];
  L --> I;
  I --> M([Response Generation]);
  M --> B;
  B --> |Client Request| A;
  N{{Admin}} --> |Admin Request| B;
  B --> |Admin Request| C;
  C --> |Admin Request| O[/Admin Management/];
  O --> |Admin Request| P{URL Routing};
  P --> |Admin Request| Q@{ shape: procs, label: "Admin View Function Execution"};
  Q --> R[Model Interaction];
  R --> Q;
  Q --> S[Template Rendering];
  S --> Q;
  Q --> T([Response Generation]);
  T --> |Admin Response| B;
  B --> |Admin Response| N;
  U[(Database)] --> J;
  U --> R;
  V@{ shape: lin-cyl, label: "Static Files" } --> K;
  V --> S;

```


## Diagram For Cloud Architecture of SociaLink
``` mermaid
graph LR
  A{{Developers}} -->|Commit & Push Code| B((GitHub));
  B --> |Trigger| C@{ shape: processes, label: "Cloud Build" }
  C --> |Push Image| D@{ shape: processes, label: "Artifact Registry" }
  C --> |Deploy| E@{ shape: processes, label: "Cloud Run" }
  D --> |Push Image| E
  E --> |Pull Image| D
  E --> F{Virtual Private Cloud Or VPC}
  F --> G@{ shape: processes, label: "Cloud SQL" }
  F --> H@{ shape: processes, label: "Cloud Storage" }
  F --> I@{ shape: processes, label: "Secret Manager" }
  F --> J@{ shape: processes, label: "AI Services" }
  G --> K[(PostgreSQL Database)]
  H --> L@{ shape: lin-cyl, label: "Static Files" }
  I --> M@{ shape: curv-trap, label: "Secrets/Environment Variables" }
  J --> N@{ shape: dbl-circ, label: "LLM 1" }
  J --> O@{ shape: dbl-circ, label: "LLM 2" }
  J --> P@{ shape: dbl-circ, label: "LLM 3" }
  D --> Q@{ shape: lin-cyl, label: "Docker Image 1" }
  D --> R@{ shape: lin-cyl, label: "Docker Image 2" }
  D --> S@{ shape: lin-cyl, label: "Docker Image 3" }
  E --> T@{ shape: lin-cyl, label: "Latest Docker Image" }
```