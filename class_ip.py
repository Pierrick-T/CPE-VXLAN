class ipaddress:
    def __init__(self, address, mask=None):
        self.ip_as_str = address
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

    def netsplit(self,new_mask):
        snet_list = []
        split_in_subs(self.get_ipstr(), self.mask, new_mask, snet_list)
        return([ipaddress(x,new_mask) for x in snet_list])

def split_in_subs(ip, mask, final_mask, list_subnets):
    if final_mask == mask:
        return list_subnets.append(ip)

    else:
        ip_as_list = ip.split(".")
        binary_ip = ''
        for i in range(4):
            binary_ip += format(int(ip_as_list[i]), '08b')
        binary_ip = binary_ip[:mask] + '1' + binary_ip[mask + 1:]
        ip2 = str(int(binary_ip[:8], 2)) + '.' + str(int(binary_ip[8:16], 2)) + '.' + str(
            int(binary_ip[16:24], 2)) + '.' + str(int(binary_ip[24:], 2))

        subnet_1 = [ip, mask + 1]
        subnet_2 = [ip2, mask + 1]
        return split_in_subs(subnet_1[0], subnet_1[1], final_mask, list_subnets), split_in_subs(subnet_2[0], subnet_2[1], final_mask, list_subnets)

