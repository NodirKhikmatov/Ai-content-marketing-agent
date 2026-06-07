# User Flow Diagrams

## 1. Onboarding Flow

```mermaid
flowchart TD
    START([Landing Page]) --> SIGNUP{Has Account?}
    SIGNUP -->|No| REGISTER[Sign Up<br/>Email or Google]
    SIGNUP -->|Yes| LOGIN[Log In]
    REGISTER --> VERIFY[Email Verification]
    VERIFY --> DASHBOARD[Empty Dashboard]
    LOGIN --> DASHBOARD
    DASHBOARD --> CREATE[Create First Project]
    CREATE --> ENTER_URL[Enter Website URL]
    ENTER_URL --> ANALYZE[Start Analysis]
    ANALYZE --> WAIT[Progress Screen<br/>2-5 min]
    WAIT --> RESULTS[Strategy Dashboard]
```

---

## 2. Website Analysis Flow

```mermaid
flowchart TD
    URL[User enters URL] --> VALIDATE{Valid URL?}
    VALIDATE -->|No| ERROR[Show validation error]
    VALIDATE -->|Yes| CRAWL[Crawl website pages]
    CRAWL --> CRAWL_OK{Crawl success?}
    CRAWL_OK -->|No| MANUAL[Fallback: Manual input form]
    CRAWL_OK -->|Yes| EXTRACT[AI extracts business intel]
    MANUAL --> EXTRACT
    EXTRACT --> COMPETITORS[Research competitors]
    COMPETITORS --> AUDIENCE[Build audience personas]
    AUDIENCE --> SEO[Generate SEO strategy]
    SEO --> CALENDAR[Create 30-day calendar]
    CALENDAR --> ASSETS[Generate content assets]
    ASSETS --> DONE[Analysis Complete]
    DONE --> NOTIFY[Notify user<br/>email + in-app]
```

---

## 3. Content Review & Approval Flow

```mermaid
flowchart TD
    LIBRARY[Content Library] --> FILTER[Filter by channel/status/date]
    FILTER --> SELECT[Select content item]
    SELECT --> VIEW[View item + assets]
    VIEW --> ACTION{User action}
    ACTION -->|Edit| EDIT[Inline editor]
    ACTION -->|Approve| APPROVE[Mark approved]
    ACTION -->|Regenerate| REGEN[Regenerate with instructions]
    ACTION -->|Reject| REJECT[Mark rejected]
    EDIT --> SAVE[Save changes]
    SAVE --> VIEW
    REGEN --> WAIT[AI regenerating...]
    WAIT --> VIEW
    APPROVE --> CALENDAR[Update calendar status]
    REJECT --> LIBRARY
```

---

## 4. Dashboard Navigation Flow

```mermaid
flowchart LR
    NAV[Sidebar Navigation]
    NAV --> HOME[Project Overview]
    NAV --> COMP[Competitors]
    NAV --> CAL[Content Calendar]
    NAV --> LIB[Content Library]
    NAV --> SEO[SEO Dashboard]
    NAV --> SET[Settings]

    HOME --> QUICK[Quick stats + recent items]
    COMP --> COMP_LIST[Competitor cards + gaps]
    CAL --> CAL_VIEW[Monthly/weekly calendar]
    LIB --> LIB_GRID[Filterable content grid]
    SEO --> SEO_TABLE[Keyword table + clusters]
    SET --> SET_PROFILE[Profile + billing + API]
```

---

## 5. Content Calendar Interaction

```mermaid
flowchart TD
    CAL[Calendar View] --> VIEW_MODE{View mode}
    VIEW_MODE -->|Month| MONTH[Monthly grid]
    VIEW_MODE -->|Week| WEEK[Weekly list]
    VIEW_MODE -->|List| LIST[All items list]
    MONTH --> CLICK[Click day/item]
    WEEK --> CLICK
    LIST --> CLICK
    CLICK --> DRAWER[Slide-out item detail]
    DRAWER --> EDIT[Edit content]
    DRAWER --> MOVE[Drag to reschedule]
    DRAWER --> STATUS[Change status]
```

---

## 6. Error & Recovery Flows

```mermaid
flowchart TD
    ANALYSIS[Analysis Running] --> FAIL{Step failed?}
    FAIL -->|No| CONTINUE[Continue pipeline]
    FAIL -->|Yes| RETRY{Retryable?}
    RETRY -->|Yes| AUTO[Auto-retry 2x]
    RETRY -->|No| PARTIAL[Save partial results]
    AUTO --> SUCCESS{Success?}
    SUCCESS -->|Yes| CONTINUE
    SUCCESS -->|No| PARTIAL
    PARTIAL --> NOTIFY_USER[Notify with error details]
    NOTIFY_USER --> MANUAL[Offer manual retry or skip step]
```

---

## 7. Phase 2: Auto-Posting Flow

```mermaid
flowchart TD
    APPROVE[Content Approved] --> SCHEDULE{Schedule?}
    SCHEDULE -->|Now| POST[Post immediately]
    SCHEDULE -->|Later| QUEUE[Add to publish queue]
    SCHEDULE -->|Skip| LIBRARY[Stay in library]
    QUEUE --> CRON[Cron checks queue]
    CRON --> CONNECTED{Account connected?}
    CONNECTED -->|No| PROMPT[Prompt to connect account]
    CONNECTED -->|Yes| PUBLISH[Publish to platform API]
    PUBLISH --> TRACK[Track post URL + metrics]
    POST --> TRACK
```
