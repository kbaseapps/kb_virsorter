input_ = "Test!!!"
        tmp_dir = self.cfg['scratch']
        input_file_name = 'input.txt'
        file_path = os.path.join(tmp_dir, input_file_name)
        with open(file_path, 'w') as fh1:
            fh1.write(input_)
        ret1 = self.impl.file_to_shock(
                    self.ctx,
                    {'file_path': file_path,
                     'make_handle': 1})[0]
        shock_id = ret1['shock_id']
        handle_id = ret1['handle']['hid']