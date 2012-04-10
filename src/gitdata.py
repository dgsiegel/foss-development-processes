#!/usr/bin/python
#
# script to generate data files from git repositories for further visualization with pgfplots
#

import sys
import os
import subprocess
from datetime import datetime

def commits_by_time(time, average_over):
  output = {}
  cmd = call_git("git log --all --format=%ai")
  for i in cmd:
    if (time == "year"):
      date = i[:4]
    elif (time == "month"):
      date = i[:7]
      date += "-01"
    else:
      date = i[:10]

    if date not in output:
      output[date] = 1
    else:
      output[date] += 1

  f = open(os.path.join(outdir, "commits_by_%s.dat" % time), "w")
  f.write("# these files were generated automatically, all changes will be lost\n")
  f.write("date commits\n")

  a = open(os.path.join(outdir, "commits_by_%s_average.dat" % time), "w")
  a.write("# these files were generated automatically, all changes will be lost\n")
  a.write("date commits\n")
  i = 0
  avg = 0

  data = sorted(output.items())
  a.write("%s %d\n" % (data[0][0],data[0][1]))

  for k, v in data:
    f.write("%s %d\n" % (k,v))
    avg += v
    if (i >= average_over - 1):
      a.write("%s %d\n" % (k,avg/average_over))
      i = 0
      avg = 0
    else:
      i += 1

  f.close()
  a.close()

def commits_by_author():
  output = {}
  authors = {}
  valid_authors = []
  author_limit = 6

  cmd = call_git("git log --all --format=\"%ai\t%aN\"")
  for i in cmd:
    (date, author) = i.split("\t")
    date = date[:7] + "-01"
    author = author.strip()

    if not output.has_key(date):
      output[date] = {}

    if author not in output[date]:
      output[date][author] = 1
    else:
      output[date][author] += 1

    if author not in authors:
      authors[author] = 1
    else:
      authors[author] += 1

  for v in sorted(authors.iteritems(), key=lambda (k,v):(v,k), reverse=True)[0:author_limit]:
    valid_authors.append(v[0])

  f = open(os.path.join(outdir, "commits_by_author.dat"), "w")
  f.write("# these files were generated automatically, all changes will be lost\n")
  f.write("# " + ", ".join(valid_authors) + "\n")
  f.write("date")
  for i in range(1, author_limit + 1):
    f.write(" commits%d" % i)
  f.write("\n")

  for k, v in sorted(output.items()):
    f.write(k)
    for a in valid_authors:
      if a in output[k]:
        f.write(" %d" % v[a])
      else:
        f.write(" 0")
    f.write("\n")

  f.close()

def authors_by_month(average_over):
  output = {}
  date = []

  cmd = call_git("git log --all --format=\"%ai\t%an\"")
  for i in cmd:
    (date, author) = i.split("\t")
    date = date[:7] + "-01"
    author = author.strip()

    if not output.has_key(date):
      output[date] = []

    if author not in output[date]:
      output[date].append(author)

  f = open(os.path.join(outdir, "authors_by_month.dat"), "w")
  f.write("# these files were generated automatically, all changes will be lost\n")
  f.write("date authors\n")
  a = open(os.path.join(outdir, "authors_by_month_average.dat"), "w")
  a.write("# these files were generated automatically, all changes will be lost\n")
  a.write("date authors\n")
  i = 0
  avg = 0

  data = sorted(output.items())
  a.write("%s %d\n" % (data[0][0],len(data[0][1])))

  for k, v in data:
    f.write("%s %d\n" % (k, len(v)))
    avg += len(v)
    if (i >= average_over - 1):
      a.write("%s %d\n" % (k,avg/average_over))
      i = 0
      avg = 0
    else:
      i += 1

  f.close()
  a.close()


def punchcard():
  output = {}
  cmd = call_git("git log --all --format=%at")
  for i,j in enumerate(cmd):
    date = datetime.fromtimestamp(int(cmd[i])).strftime("%H %A")
    if date not in output:
      output[date] = 1
    else:
      output[date] += 1

  f = open(os.path.join(outdir, "punchcard.dat"), "w")
  f.write("# these files were generated automatically, all changes will be lost\n")
  f.write("hour day commits\n")

  for k, v in sorted(output.items()):
    f.write("%s %d\n" % (k,v))

  f.close()

def call_git(arg):
  cmd = []
  for d in gitdirs:
    os.chdir(d)
    cmd.extend(os.popen(arg).readlines())
  return cmd

def unique(seq, idfun=None):
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

if len(sys.argv) < 3:
  print "Usage: gitdata <git paths...> <output path>"
  sys.exit(1)

gitdirs = sys.argv[1:-1]
for d in gitdirs:
  if not os.path.isdir(d) and not os.path.exists(os.path.join(d, ".git")):
    print d + " does not look like a git directory"
    sys.exit(1)

outdir = os.path.abspath(sys.argv[-1])
if not os.path.isdir(outdir):
  print outdir + " does not exist"
  sys.exit(1)

commits_by_time("year", 3.0)
commits_by_time("month", 3.0)
commits_by_author()
authors_by_month(3.0)
punchcard()
