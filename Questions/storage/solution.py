class Filesystem:
  def __init__(self, capacity = float('inf')):
    self.files = {}
    self.capacity = capacity
    self.usage = 0

  def add(self, name, size):
    if name in self.files: return "false"
    if size + self.usage > self.capacity : return "false"
    self.usage += size
    self.files[name] = size
    return "true"

  def get(self, name):
    if name not in self.files: return ""
    # print('getting' , self.files[name])
    return str(self.files[name])

  def delete(self,name):
    if name not in self.files: return ""
    size = self.files.pop(name)
    self.usage -= size
    return str(size)

  def n_largest(self, prefix, n):
    common = []
    for f, s in self.files.items():
      if f.startswith(prefix):
        common.append((-s, f))
    common.sort()
    print("sorted list" , common)
    return ", ".join([f'{y}({-x})' for x,y in common[:n]])
  
  def merge(self, user2):
    self.capacity += user2.capacity
    self.usage += user2.usage
    self.files.update(user2.files)
  
    
class User:
  def __init__(self):
    self.users = {}
    self.users["admin"] = Filesystem()
    self.backups = {}
    self.mapping = {}
  
  def add_users(self, userID, capacity):
    if userID in self.users: return "false"
    self.users[userID] = Filesystem(capacity)
    return "true"

  def add_file_by(self, userID, name, size):
    if name in self.mapping: return ""
    u = self.users[userID]
    o = u.add(name, size)
    if o == "false": return ""
    self.mapping[name] = userID
    return str(u.capacity - u.usage)
  
  def merge(self, user1, user2):
    if user1 not in self.users or user2 not in self.users: return ""
    u2 = self.users.pop(user2)
    self.users[user1].merge(u2)
    return str(self.users[user1].capacity - self.users[user1].usage)

  def backup(self, user):
    if user not in self.users: return ""
    copy = {}
    u = self.users[user]
    for f,s in u.files.items():
      copy[f] = s
    self.backups[user] = (copy, u.capacity, u.usage)
    return str(len(copy))
    
  def remove(self, user):
    for f in self.users[user].files:
      self.mapping.pop(f)
  
  def bulkrestore(self, user, files):
    fs = self.users[user].files 
    cap = 0
    ans = 0
    for f, c in files.items():
      if f in self.mapping:
        continue
      ans += 1
      self.mapping[f] = user
      fs[f] = c
      cap += c
    self.users[user].usage = cap
    return ans 

  def restore(self, user):
    if user not in self.users: return ""
    if user not in self.backups:
      self.remove(user)
      self.users[user].files = {}
      self.users[user].usage = 0
      return "0"
    
    self.remove(user)
    fs, *other = self.backups[user]
    c = self.bulkrestore(user, fs)

    return str(c)
  
  def get(self, name):
    if name not in self.mapping: return ""
    user = self.mapping[name] 
    return self.users[user].get(name)

  def delete(self, name):
    if name not in self.mapping: return ""
    user = self.mapping[name]
    self.mapping.pop(name)
    return self.users[user].delete(name)
  
  def n_largest(self, prefix, n):
    return self.users['admin'].n_largest(prefix, n)
  
class Solution:
  u = User()
  fs = u.users["admin"]
  ans = []

  def test(self, input):
    global u, fs, ans
    u = User()
    fs = Filesystem()
    ans = []
    for i in input:
      output = self.helper(i)
      print(i,':', output)
      ans.append(output)
      
    print("answer is :", ans)
    return ans

  def helper(self, f):
    global fs, ans, u
    s = f[0]
    if s == "ADD_FILE":
      val= (u.add_file_by('admin', f[1], int(f[2])))
      if val != "": return "true"
      else: return "false"
    elif s == "GET_FILE_SIZE":
      return (u.get(f[1]))
    elif s == "DELETE_FILE":
      return (u.delete(f[1]))
    elif s == "GET_N_LARGEST":
      return (u.n_largest(f[1], int(f[2])))
    elif s == "ADD_USER":
      return (u.add_users(f[1], int(f[2])))
    elif s == "ADD_FILE_BY":
      return (u.add_file_by(f[1], f[2], int(f[3])))
    elif s == "MERGE_USER":
      return (u.merge(f[1], f[2]))
    elif s =="BACKUP_USER":
      return (u.backup(f[1]))
    elif s =="RESTORE_USER":
      return (u.restore(f[1]))


s = Solution()

level1 = [
  ["ADD_FILE", "/dir1/dir2/file.txt", "10"], 
  ["ADD_FILE", "/dir1/dir2/file.txt", "5"],
  ["GET_FILE_SIZE", "/dir1/dir2/file.txt"],
  ["DELETE_FILE", "/not-existing.file"],
  ["DELETE_FILE", "/dir1/dir2/file.txt"],
  ["GET_FILE_SIZE", "/not-existing.file"]
]

assert s.test(level1) == ["true", "false", "10", "", "10", ""]

print('========== PASSED LEVEL 1 ============')

level2 = [
  ["ADD_FILE", "/dir/file1.txt", "5"],
  ["ADD_FILE", "/dir/file2", "20"],
  ["ADD_FILE", "/dir/deeper/file3.mov", "9"],
  ["GET_N_LARGEST", "/dir", "2"],
  ["GET_N_LARGEST", "/dir/file", "3"],
  ["GET_N_LARGEST", "/another_dir", "5"],
  ["ADD_FILE", "/big_file.mp4", "20"],
  ["GET_N_LARGEST", "/", "2"]
]

assert s.test(level2) == ["true", "true", "true", "/dir/file2(20), /dir/deeper/file3.mov(9)", "/dir/file2(20), /dir/file1.txt(5)", "", "true", "/big_file.mp4(20), /dir/file2(20)"]
print('========== PASSED LEVEL 2 ============')


level3 = [
  ["ADD_USER", "user1", "200"],
  ["ADD_USER", "user1", "100"],
  ["ADD_FILE_BY", "user1", "/dir/file.med", "50"],
  ["ADD_FILE_BY", "user1", "/big.blob", "140"],
  ["ADD_FILE_BY", "user1", "/file-small", "20"],
  ["ADD_FILE", "/dir/admin_file", "300"],
  ["ADD_USER", "user2", "110"],
  ["ADD_FILE_BY", "user2", "/dir/file.med", "45"],
  ["ADD_FILE_BY", "user2", "/new_file", "50"],
  ["MERGE_USER", "user1", "user2"]
]

assert s.test(level3) ==["true", "false", "150", "10", "", "true", "true", "", "60", "70"]

print('========== PASSED LEVEL 3 ============')
level4 =[
  ["ADD_USER", "user", "100"],
  ["ADD_FILE_BY", "user", "/dir/file1", "50"],
  ["ADD_FILE_BY", "user", "/file2.txt", "30"],
  ["RESTORE_USER", "user"],
  ["ADD_FILE_BY", "user", "/file3.mp4", "60"],
  ["ADD_FILE_BY", "user", "/file4.txt", "10"],
  ["BACKUP_USER", "user"],
  ["DELETE_FILE", "/file3.mp4"],
  ["DELETE_FILE", "/file4.txt"],
  ["ADD_FILE_BY", "user", "/dir/file5.new", "20"],
  ["RESTORE_USER", "user"]
]

assert s.test(level4) == ["true", "50", "20", "0", "40", "30", "2", "60", "10", "80", "2"]