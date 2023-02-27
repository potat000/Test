update station_pile set costType = 2 where costType = 'kWh';
update station_pile set costType = 1 where costType = 'Free';
update station_pile set costType = 3 where costType = 'Hour';
update finance_greenpointpromotion set greenPointAmount = 20556 where greenPointAmount >= 32767;
update finance_greenpointcompanybalance set greenPointBalanceOnfly = 15273 where greenPointBalanceOnfly >= 32767;
update finance_greenpointcompanybalance set greenPointBalance = 16999 where greenPointBalance >= 32767;