# 🍽️ Restaurant AI Agent with MCP Server

An intelligent restaurant ordering system powered by **DSPy ReAct Agent** and **Model Context Protocol (MCP)**. This project enables natural language conversations with customers to take orders, manage menu items, send orders to the kitchen via email, and save order records to Excel.

## 📋 Overview

| Component | Description |
|-----------|-------------|
| `mcp_server_res.py` | MCP Server exposing restaurant tools (menu, orders, email, Excel) |
| `resAgent.py` | DSPy ReAct Agent chatbot that uses MCP tools to interact with customers |

### Architecture

```
┌─────────────────┐     MCP Protocol      ┌──────────────────────┐
│   resAgent.py   │◄────────────────────► │  mcp_server_res.py   │
│  (DSPy ReAct)   │    stdio transport    │   (FastMCP Server)   │
│                 │                       │                      │
│  • Chat with    │                       │  • fetch_menu()      │
│    customer     │                       │  • calculate_total() │
│  • Intent       │                       │  • create_order()    │
│    detection    │                       │  • send_to_kitchen() │
│  • Order        │                       │  • save_in_excel()   │
│    tracking     │                       │                      │
└─────────────────┘                       └──────────────────────┘
                                                    │
                    ┌───────────────────────────────┼───────────────────────┐
                    │                               │                       │
                    ▼                               ▼                       ▼
             📧 Gmail SMTP                   📊 orders.xlsx           🍔 Menu DB
           (Kitchen Notifications)          (Order Records)         (In-Memory)
```

## ✨ Features

### MCP Server Tools (`mcp_server_res.py`)

| Tool | Description |
|------|-------------|
| `fetch_menu(category)` | Fetch menu items by category (appetizer, main, dessert, drink, all) |
| `calculate_total(items)` | Calculate subtotal, tax (10%), and grand total for order items |
| `create_order(...)` | Create a new order with customer info and items |
| `send_to_kitchen(order_id)` | Send order to kitchen via email notification |
| `save_in_excel(...)` | Save order details to `orders.xlsx` with formatted headers |

### Agent Capabilities (`resAgent.py`)

- 🗣️ **Natural Language Understanding** - Understands customer intent from conversational messages
- 📋 **Menu Browsing** - Shows menu items by category with prices and descriptions
- 🛒 **Order Management** - Takes orders, handles modifications, special requests
- 👤 **Customer Info Collection** - Collects name, table/location, phone number
- ✅ **Order Confirmation** - Confirms order details before finalizing
- 📤 **Kitchen Integration** - Sends finalized orders to kitchen via email

### Menu Items (Sample)

| Category | Item | Price |
|----------|------|-------|
| Appetizer | Bruschetta | $8.99 |
| Appetizer | Buffalo Wings | $12.99 |
| Main | Grilled Salmon | $24.99 |
| Main | Chicken Alfredo Pasta | $18.99 |
| Dessert | Chocolate Lava Cake | $8.99 |
| Drink | Fresh Lemonade | $4.99 |

## 🚀 Installation

### Prerequisites

- Python 3.10+
- Gmail account (for kitchen notifications)

### Setup

1. **Clone or navigate to the project directory**

2. **Install dependencies**
   ```bash
   pip install dspy mcp openpyxl pydantic python-dotenv
   ```

3. **Create `.env` file** in the `Resturant` folder:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   SENDER_EMAIL=your_gmail@gmail.com
   SENDER_PASSWORD=your_app_password
   ```
   
   > **Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## 📖 Usage

### Running the Chatbot

```bash
cd Resturant
python resAgent.py
```

### Example Conversation

```
Restaurant Chatbot
==================================================
Type 'quit' to exit

You: Hi, I'd like to see the menu
Agent: Welcome! Here's our menu. We have appetizers like Bruschetta ($8.99) 
       and Buffalo Wings ($12.99), main courses including Grilled Salmon ($24.99) 
       and Chicken Alfredo Pasta ($18.99), plus desserts and drinks!

You: I'll have the salmon and a lemonade
Agent: Great choices! That's Grilled Salmon ($24.99) and Fresh Lemonade ($4.99). 
       May I have your name for the order?

You: My name is Ahmed, table 5, phone 555-1234
Agent: Perfect, Ahmed! Your order is:
       • Grilled Salmon - $24.99
       • Fresh Lemonade - $4.99
       Subtotal: $29.98 | Tax: $3.00 | Total: $32.98
       Shall I confirm and send this to the kitchen?

You: Yes, confirm it
Agent: Order confirmed! Your order has been sent to the kitchen. 
       It will be ready shortly. Thank you, Ahmed!

You: quit
Thanks for visiting!
```

## 📁 Project Structure

```
Resturant/
├── mcp_server_res.py    # MCP Server with restaurant tools
├── resAgent.py          # DSPy ReAct Agent chatbot
├── orders.xlsx          # Generated Excel file with order history
├── .env                 # Environment variables (create this)
└── README.md            # This file
```

## 🔧 Configuration

### Agent States

The agent tracks conversation state:

| State | Description |
|-------|-------------|
| `GREET` | Initial greeting |
| `VIEW_MENU` | Customer is browsing menu |
| `PLACE_ORDER` | Customer is placing order |
| `MODIFY_ORDER` | Customer is modifying order |
| `PROVIDE_INFO` | Collecting customer details |
| `CONFIRM_ORDER` | Confirming order before submission |
| `FINALIZED` | Order sent to kitchen |
| `CANCEL` | Order cancelled |

### Customizing the Menu

Edit the `menu_database` dictionary in `mcp_server_res.py`:

```python
menu_database = {
    "your_item_id": MenuItem(
        item_id="your_item_id",
        name="Item Name",
        category="main",  # appetizer, main, dessert, drink
        description="Description here",
        price=19.99,
        ingredients=["ingredient1", "ingredient2"],
        dietary_tags=["vegetarian", "gluten-free"],
        available=True,
        preparation_time=20,  # minutes
        popularity_score=8    # 1-10
    ),
}
```

## 🛠️ Development

### Running MCP Server Standalone

```bash
python mcp_server_res.py
```

### Changing LLM Provider

In `resAgent.py`, modify the LM configuration:

```python
# For Gemini (default)
lm = dspy.LM(model="gemini/gemini-2.5-flash", api_key=GEMINI_API_KEY, temperature=0.8)

# For Claude
lm = dspy.LM(model="anthropic/claude-3-haiku", api_key=CLAUDE_API_KEY)

# For OpenAI
lm = dspy.LM(model="openai/gpt-4", api_key=OPENAI_API_KEY)
```

## 📧 Email Configuration

The system sends order notifications to the kitchen via Gmail SMTP:

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password at [Google Account > Security > App Passwords](https://myaccount.google.com/apppasswords)
3. Add to `.env`:
   ```env
   SENDER_EMAIL=your_gmail@gmail.com
   SENDER_PASSWORD=xxxx xxxx xxxx xxxx
   ```

## 📊 Excel Output

Orders are saved to `orders.xlsx` with the following columns:

| Order ID | Date | Customer Name | Phone Number | Location | Items |
|----------|------|---------------|--------------|----------|-------|
| ORD-1 | 2026-01-02 20:30:00 | Ahmed | 555-1234 | Table 5 | main_001, drink_001 |

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "No MCP tools found" | Ensure `mcp_server_res.py` is in the same directory |
| Email fails to send | Check Gmail App Password and 2FA settings |
| Excel permission error | Close `orders.xlsx` if open in Excel |
| API key errors | Verify `.env` file exists with correct keys |



## 🤝 Contributing

Feel free to extend the menu, add new tools, or improve the agent's conversational abilities!
