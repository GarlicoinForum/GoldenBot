CREATE TABLE `cmc_exchanges` (
	`timestamp`	INTEGER NOT NULL UNIQUE,
	`Trade Satoshi_GRLC/BTC`	REAL NOT NULL,
    `CoinFalcon_GRLC/BTC`	REAL NOT NULL,
    `CryptoBridge_GRLC/BTC`	REAL NOT NULL,
    `Nanex_GRLC/NANO`	REAL NOT NULL,
    `Trade Satoshi_GRLC/LTC`	REAL NOT NULL,
    `Trade Satoshi_GRLC/BCH`	REAL NOT NULL,
    `Trade Satoshi_GRLC/DOGE`	REAL NOT NULL,
    `Trade Satoshi_GRLC/USDT`	REAL NOT NULL,
    `CoinFalcon_GRLC/ETH`	REAL NOT NULL,
	PRIMARY KEY(`timestamp`)
);
