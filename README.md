# Interactive Feedback MCP

**[English Version / 英文版本](README-eng.md)**

由 Fábio Ferreira ([@fabiomlferreira](https://x.com/fabiomlferreira)) 開發。
請查看 [dotcursorrules.com](https://dotcursorrules.com/) 以獲得更多 AI 開發增強功能。

簡單的 [MCP Server](https://modelcontextprotocol.io/)，可在 AI 輔助開發工具（如 [Cursor](https://www.cursor.com)）中啟用人機協作工作流程。此伺服器允許您執行命令、查看其輸出，並直接向 AI 提供文字回饋。它也與 [Cline](https://cline.bot) 和 [Windsurf](https://windsurf.com) 相容。

![Interactive Feedback UI - Main View](https://github.com/noopstudios/interactive-feedback-mcp/blob/main/.github/interactive_feedback_1.jpg?raw=true)
![Interactive Feedback UI - Command Section Open](https://github.com/noopstudios/interactive-feedback-mcp/blob/main/.github/interactive_feedback_2.jpg)

## Prompt 工程

為獲得最佳效果，請將下列內容加入你的 AI 助理自訂提示中，可加在規則或直接於提示內（例如 Cursor）：
經過我實測，原本作者的 prompt 不一定每次對話都會出現，有時 LLM 會自動結束對話，以下是我優化過的 prompt，實測會問到天荒地老，有種 Cursor VIP 感覺，fast request 富翁用不完

```mardown
# MCP Interactive Feedback 規則

1. 在任何流程、任務、對話進行時，無論是詢問、回覆、或完成階段性任務，皆必須呼叫 MCP interactive_feedback。
2. 每當收到使用者回饋，若回饋內容非空，必須再次呼叫 MCP interactive_feedback，並根據回饋內容調整行為。
3. 僅當使用者明確表示「結束」或「不再需要互動」時，才可停止呼叫 MCP interactive_feedback，流程才算結束。
4. 除非收到結束指令，否則所有步驟都必須重複呼叫 MCP interactive_feedback。
```

這將確保您的 AI 助手使用此 MCP 伺服器在將任務標記為完成之前請求使用者回饋。

## 💡 為什麼使用這個？

通過引導助手與使用者確認而不是分支到推測性的高成本工具呼叫，此模組可以大幅減少平台（如 Cursor）上的高級請求數量（例如，OpenAI 工具調用）。在某些情況下，它有助於將原本需要多達 25 次工具呼叫的操作整合為單一的、具有回饋感知的請求——節省資源並提高效能。

## 配置

此 MCP 伺服器使用 Qt 的 `QSettings` 來按專案儲存配置。這包括：

- 要執行的命令。
- 是否在該專案的下次啟動時自動執行命令（請參閱「下次執行時自動執行」核取方塊）。
- 命令區段的可見性狀態（顯示/隱藏）（這會在切換時立即儲存）。
- 視窗幾何和狀態（一般 UI 偏好設定）。

這些設定通常儲存在平台特定的位置（例如，Windows 上的登錄檔、macOS 上的 plist 檔案、Linux 上 `~/.config` 或 `~/.local/share` 中的配置檔案），在組織名稱「FabioFerreira」和應用程式名稱「InteractiveFeedbackMCP」下，每個專案目錄都有唯一的群組。

UI 中的「儲存配置」按鈕主要儲存當前輸入到命令輸入欄位中的命令以及活動專案的「下次執行時自動執行」核取方塊的狀態。命令區段的可見性會在您切換時自動儲存。一般視窗大小和位置會在應用程式關閉時儲存。

## 安裝 (Cursor)

![Instalation on Cursor](https://github.com/noopstudios/interactive-feedback-mcp/blob/main/.github/cursor-example.jpg?raw=true)

1.  **先決條件：**
    - Python 3.11 或更新版本。
    - [uv](https://github.com/astral-sh/uv) (Python 套件管理器)。使用以下方式安裝：
      - Windows: `pip install uv`
      - Linux/Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2.  **取得程式碼：**
    - 複製此儲存庫：
      `git clone https://github.com/noopstudios/interactive-feedback-mcp.git`
    - 或下載原始碼。
3.  **導航到目錄：**
    - `cd path/to/interactive-feedback-mcp`
4.  **安裝相依性：**
    - `uv sync` (這會建立虛擬環境並安裝套件)
5.  **執行 MCP Server：**
    - `uv run server.py`
6.  **在 Cursor 中配置：**

    - Cursor 通常允許在其設定中指定自定義 MCP 伺服器。您需要將 Cursor 指向此執行中的伺服器。確切的機制可能會有所不同，因此請查閱 Cursor 的文件以了解如何添加自定義 MCP。
    - **手動配置（例如，透過 `mcp.json`）**
      **請記住將 `/Users/fabioferreira/Dev/scripts/interactive-feedback-mcp` 路徑更改為您在系統上複製儲存庫的實際路徑。**

      ```json
      {
        "mcpServers": {
          "interactive-feedback-mcp": {
            "command": "uv",
            "args": [
              "--directory",
              "/Users/fabioferreira/Dev/scripts/interactive-feedback-mcp",
              "run",
              "server.py"
            ],
            "timeout": 600,
            "autoApprove": ["interactive_feedback"]
          }
        }
      }
      ```

    - 在 Cursor 中配置時，您可能會使用像 `interactive-feedback-mcp` 這樣的伺服器識別碼。

### 對於 Cline / Windsurf

類似的設定原則適用。您需要在相應工具的 MCP 設定中配置伺服器命令（例如，`uv run server.py` 並使用正確的 `--directory` 參數指向專案目錄），使用 `interactive-feedback-mcp` 作為伺服器識別碼。

## 開發

要在開發模式下執行伺服器並使用 web 介面進行測試：

```sh
uv run fastmcp dev server.py
```

這將開啟一個 web 介面，允許您與 MCP 工具互動進行測試。

## 可用工具

以下是 AI 助手如何呼叫 `interactive_feedback` 工具的範例：

```xml
<use_mcp_tool>
  <server_name>interactive-feedback-mcp</server_name>
  <tool_name>interactive_feedback</tool_name>
  <arguments>
    {
      "project_directory": "/path/to/your/project",
      "summary": "I've implemented the changes you requested and refactored the main module."
    }
  </arguments>
</use_mcp_tool>
```

## 致謝與聯絡

如果您覺得這個 Interactive Feedback MCP 有用，表達感謝的最佳方式是在 [X @fabiomlferreira](https://x.com/fabiomlferreira) 上關注 Fábio Ferreira。

如有任何問題、建議，或者您只是想分享您的使用方式，歡迎在 X 上聯絡！

另外，請查看 [dotcursorrules.com](https://dotcursorrules.com/) 以獲得更多增強您的 AI 輔助開發工作流程的資源。

---

**繁體中文翻譯與本地化：** [https://jackle.pro/](https://jackle.pro/)
