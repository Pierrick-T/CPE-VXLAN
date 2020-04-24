class ipaddress:
    def __init__(self, address, mask=None):
        #  define the ip as a list
        if mask is not None:
            self.address = []
            buffer = ''
            for x in address:
                if x == '.':
                    self.address.append(int(buffer))
                    buffer = ''
                else:
                    buffer += x
            self.address.append(int(buffer))

            # define the mask
            if type(mask) == int:
                self.mask = mask
            else:
                self.mask = []
                buffer = ''
                for x in mask:
                    if x == '.':
                        self.mask.append(int(buffer))
                        buffer = ''
                    else:
                        buffer += x
                self.mask.append(int(buffer))
        if mask is None:
            self.address = []
            self.mask = []
            buffer = ''
            for x in address:
                if x == '.':
                    self.address.append(int(buffer))
                    buffer = ''
                elif x == '/':
                    self.address.append(int(buffer))
                    self.mask = (int(address[address.index('/')+1:]))
                    break
                else:
                    buffer += x

    def get_ipstr(self):
        ip_str = ''
        for x in self.address:
            ip_str += str(x)
            ip_str += '.'
        return ip_str[:-1]

    def get_ipmstr(self):
        ip_str = self.get_ipstr()
        ip_str += '/' + str(self.mask)
        return ip_str

    def get_mask(self):
        mask = ['0' for _ in range(32)]
        k = 0
        while k < self.mask:
            mask[k] = '1'
            k += 1

        buffer2 = ''
        for i in range(4):
            buffer1 = ''
            for j in range(8):
                buffer1 += mask[8*i+j]
            buffer2 += str(int(buffer1, 2)) + '.'
        return buffer2[:-1]

    def __copy__(self):
        return type(self)(self.get_ipstr(), str(self.mask))
