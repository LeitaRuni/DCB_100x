EIP712_TYPES = {
    "EIP712Domain": [
        {"name": 'name',"type": 'string'},
        {"name": 'version',"type": 'string'},
        {"name": 'chainId',"type": 'uint256'},
        {"name": 'verifyingContract', "type": 'address'},
    ],
    "LoginMessage": [
        {"name": "account", "type": "address"},
        {"name": "message", "type": "string"},
        {"name": "timestamp", "type": "uint64"}
    ],
    "Withdraw": [
        {"name": "account", "type": "address"},
        {"name": "subAccountId", "type": "uint8"},
        {"name": "asset", "type": "address"},
        {"name": "quantity", "type": "uint128"},
        {"name": "nonce", "type": "uint64"}
    ],
    "Order": [
        {"name": "account", "type": "address"},
        {"name": "subAccountId", "type": "uint8"},
        {"name": "productId", "type": "uint32"},
        {"name": "isBuy", "type": "bool"},
        {"name": "orderType", "type": "uint8"},
        {"name": "timeInForce", "type": "uint8"},
        {"name": "expiration", "type": "uint64"},
        {"name": "price", "type": "uint128"},
        {"name": "quantity", "type": "uint128"},
        {"name": "nonce", "type": "uint64"}
    ],
    "ApproveSigner": [ 
        {"name": "account", "type": "address"},
        {"name": "subAccountId", "Type": "uint8"},
        {"name": "approvedSigner", "type": "address"},
        {"name": "isApproved", "type": "bool"},
        {"name": "nonce", "type": "uint64"}
    ],
    "SignedAuthentication": [
        {"name": "account", "type": "address"},
        {"name": "subAccountId", "type": "uint8"},
    ]
}

SECONDS_PER_TIMESTAMP = {
    "1m": 60,       
    "5m": 300,      
    "15m": 900,     
    "30m": 1800,    
    "1h": 3600,     
    "2h": 7200,     
    "4h": 14400,    
    "8h": 28800,    
    "1d": 86400,    
    "3d": 259200,   
    "1w": 604800    
}

LIMITS_PER_TIMESTAMP = {
    "1m": 1000,
    "5m": 288 ,
    "15m": 96,
    "30m": 48,
    "1h": 24,
    "2h": 12,
    "4h": 6,
    "8h": 3,
    "1d": 1,
    "3d": 0,
    "1w": 0
}

LIMIT = 0
LIMIT_MAKER = 1
MARKET  = 2
STOP_LOSS  = 3
STOP_LOSS_LIMIT  = 4
TAKE_PROFIT  = 5
TAKE_PROFIT_LIMIT  = 6

GTC = 0 
FOK = 1  
IOC = 2

PROD = "prod"
TESTNET = "testnet"
DEVNET = "local"

