ORDER_BASIC_ERP_EXCEL_FIELD_MAPPING = {
"순번" : None, 
"사이트" : "FLD_DSP",
"수취인명" : "RECEIVE_NAME",
"금액" : None,
"주문번호" : "ORDER_ID",
"제품명" : None, 
"수량" : "SALE_CNT",
"전화번호1" : "RECEIVE_CEL",
"전화번호2" : "RECEIVE_TEL",
"수취인주소" : "RECEIVE_ADDR", 
"우편번호" : "RECEIVE_ZIPCODE",
"선/착불" : "DELIVERY_METHOD_STR",
"상품번호" : "MALL_PRODUCT_ID",
"배송메시지" : "DELV_MSG",
"정산예정금액" : lambda data : int((getattr(data, "MALL_WON_COST", 0))) *  int(getattr(data, "SALE_CNT", 0)),
"서비스이용료" : lambda data : int(getattr(data, "PAY_COST", 0)) - int(getattr(data, "MALL_WON_COST", 0)) * int(getattr(data, "SALE_CNT", 0)),
"장바구니번호" : "MALL_ORDER_ID",
"운송장번호" : None,
"운임비타입" : None,
"판매자관리코드" : None,
"금액[배송비미포함]" : "PAY_COST",
"배송비" : "DELV_COST", 
"사방넷품번코드" : "PRODUCT_ID",
"사방넷주문번호" : "IDX",
"수집상품명" : "PRODUCT_NAME",
"수집옵션" : "SKU_VALUE"
}