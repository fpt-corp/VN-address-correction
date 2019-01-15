# Sửa địa chỉ 
## API
Sửa lại địa chỉ định dạng ...xã/thị trấn...quận/huyện/tp...tỉnh/tp...
Địa chỉ đầu vào chỉ chứa kí tự viết thường và dấu cách (không chứa dấu phẩy). API sẽ tự sửa lỗi và thêm dấu phẩy
```
from address_correction import AddressCorrection
address_correction = AddressCorrection()
address_correction.address_correction('thọ nghip xuân trương nam dịnh')
# return ('thọ nghiệp, xuân trường, nam định', 1.6)
# giá trị trả về đầu là địa chỉ đã sửa, giá trị trả về thứ 2 là chỉ số đo sự sai khác giữa địa chỉ đầu vào và địa chỉ trả về. Giá trị trả về là -1 nếu không thể sửa được
```

## Những lỗi đã sửa được

* Lỗi thiếu dấu, sai dấu, sai vị trí dấu
* Lỗi thiếu kí tự, sai kí tự

## Những lỗi chưa sửa được

* Các từ sai vị trí, các từ sai trường (Sai vị trí từ giữa quê quán địa chỉ và thời hạn (không thời hạn))
* Dấu cách bị thiếu giữa phần ngăn cách xã - huyện, huyện - tỉnh
* Các địa danh dưới cấp xã, địa danh không có trong list đã có, các địa danh nước ngoài (Trung Quốc, Campuchia,...)
* Các lỗi được sửa và không sửa được lưu trong file address_correct.csv, home_correct.csv