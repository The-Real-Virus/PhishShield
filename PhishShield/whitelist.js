// The "Mega-Whitelist" - Top global sites that should NEVER be flagged.
const TRUSTED_DOMAINS_SET = new Set([
    // --- Original Top 30 ---
    'google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'wikipedia.org',
    'twitter.com', 'linkedin.com', 'instagram.com', 'netflix.com', 'microsoft.com',
    'github.com', 'whatsapp.com', 'apple.com', 'yahoo.com', 'bing.com',
    'live.com', 'office.com', 'twitch.tv', 'spotify.com', 'adobe.com',
    'paypal.com', 'stackoverflow.com', 'reddit.com', 'tiktok.com', 'zoom.us',
    'salesforce.com', 'canva.com', 'ebay.com', 'dropbox.com', 'openai.com',

    // --- AI & ML Platforms ---
    'chatgpt.com', 'deepseek.com', 'kimi.ai', 'x.ai', 'anthropic.com',
    'claude.ai', 'gemini.google.com', 'bard.google.com', 'ai.google.com',
    'perplexity.ai', 'huggingface.co', 'stability.ai', 'midjourney.com',
    'runwayml.com', 'jasper.ai', 'copy.ai', 'notion.ai', 'fireworks.ai',
    'cohere.com', 'replicate.com', 'grok.com', 'kimi.com', 'moonshot.ai',
    'chat.deepseek.com', 'ollama.com', 'llama.com', 'pinecone.io', 'chroma.dev',
    'modal.com',

    // --- Cloud & Infrastructure ---
    'aws.amazon.com', 'azure.microsoft.com', 'cloud.google.com', 'cloudflare.com',
    'fastly.com', 'akamai.com', 'digitalocean.com', 'heroku.com', 'vercel.com',
    'netlify.com', 'ibm.com', 'oracle.com', 'vmware.com', 'alibaba.cloud.com',
    'hostinger.com', 'railway.app', 'render.com', 'fly.io', 'supabase.com',
    'firebase.google.com', 'appwrite.io', 'pocketbase.io', 'pages.dev',
    'workers.dev',

    // --- Developer Tools & Platforms ---
    'gitlab.com', 'bitbucket.org', 'docker.com', 'npmjs.com', 'pypi.org',
    'maven.apache.org', 'gradle.org', 'jetbrains.com', 'visualstudio.com',
    'code.visualstudio.com', 'stackexchange.com', 'codepen.io', 'codesandbox.io',
    'jsfiddle.net', 'python.org', 'cpanel.net', 'nginx.org', 'apache.org',
    'replit.com', 'stackblitz.com', 'glitch.com', 'gitpod.io', 'coder.com',
    'jdoodle.com', 'onlinegdb.com', 'programiz.com', 'codedamn.com',
    'pythonanywhere.com', 'codewars.com', 'leetcode.com', 'hackerrank.com',
    'codechef.com', 'kaggle.com', 'cursor.sh', 'sourcegraph.com', 'linear.app',
    'height.app', 'raycast.com', 'postman.com', 'swagger.io', 'jwt.io',
    'regex101.com', 'cyberchef.io', 'git-scm.com', 'cli.github.com',
    'gitkraken.com', 'sourcetree.app',

    // --- Communication & Collaboration ---
    'slack.com', 'discord.com', 'telegram.org', 'signal.org', 'skype.com',
    'teams.microsoft.com', 'meet.google.com', 'webex.com', 'qq.com',
    'wechat.com', 'obsproject.com', 'calendly.com', 'messenger.com', 'wa.me',
    'docomo.ne.jp', 'mattermost.com', 'zulip.com',

    // --- Productivity & Design ---
    'notion.so', 'figma.com', 'miro.com', 'asana.com', 'monday.com',
    'trello.com', 'atlassian.com', 'jira.com', 'confluence.com', 'airtable.com',
    'typeform.com', 'surveymonkey.com', 'lovable.dev', 'framer.com',
    'webflow.com', 'dribbble.com', 'behance.net', 'uiverse.io', 'land-book.com',
    'lapa.ninja',

    // --- E-commerce & Marketplaces ---
    'walmart.com', 'target.com', 'alibaba.com', 'aliexpress.com', 'etsy.com',
    'shopify.com', 'rakuten.co.jp', 'mercadolibre.com', 'flipkart.com',
    'bestbuy.com', 'costco.com', 'homedepot.com', 'temu.com', 'shein.com',
    'booking.com', 'samsung.com', 'wildberries.ru', 'ozon.ru', 'avito.ru',

    // --- Payment & Financial Services ---
    'stripe.com', 'square.com', 'wise.com', 'revolut.com', 'coinbase.com',
    'binance.com', 'visa.com', 'mastercard.com', 'americanexpress.com',
    'intuit.com', 'bitstamp.com', 'forex.com', 'investing.com', 'dailyforex.com',
    'financemagnates.com', 'charlesschwab.com', 'activtrades.com',

    // --- News & Media ---
    'bloomberg.com', 'reuters.com', 'cnn.com', 'bbc.com', 'nytimes.com',
    'wsj.com', 'forbes.com', 'theguardian.com', 'nbcnews.com', 'abcnews.go.com',
    'yahoo.co.jp', 'news.yahoo.co.jp', 'mail.ru', 'ya.ru', 'yandex.ru',
    'globo.com', 'rutube.ru', 'espn.com', 'bbc.co.uk', 'imdb.com', 'weather.com',
    'foxnews.com', 'dailymail.co.uk', 'independent.co.uk', 'usatoday.com',
    'huffingtonpost.com', 'businessinsider.com', 'uol.com.br', 'abril.com.br',
    'ig.com.br', 'estadao.com.br', 'correios.com.br', 'ft.com', 'apnews.com',
    'ap.org', 'dw.com', 'pressgazette.co.uk', 'cbsnews.com', 'aljazeera.com', 'fastcompany.com',
    'allaboutcookies.org', 'bmj.com', 'business.site', 'huffpost.com', 'tripod.com',

    // --- Search & Portals ---
    'duckduckgo.com', 'yandex.com', 'baidu.com', 'naver.com', 'aol.com',
    'msn.com', 'ask.com', 'startpage.com', 'brave.com', 'netvibes.com',
    'feedburner.com', 'daum.net',

    // --- Gaming ---
    'steampowered.com', 'epicgames.com', 'ea.com', 'activision.com',
    'nintendo.com', 'playstation.com', 'xbox.com', 'roblox.com', 'minecraft.net',
    'discord.gg', 'rockpapershotgun.com', 'gameinformer.com', 'steamcommunity.com',
    'supercell.com',

    // --- Streaming & Entertainment ---
    'disney.com', 'hulu.com', 'hbomax.com', 'primevideo.com', 'paramount.com',
    'peacocktv.com', 'pandora.com', 'soundcloud.com', 'bilibili.com',
    'crackle.com', 'pluto.tv', 'moviesjoy.to', 'flixrave.to', 'f2movies.to',
    'gomovies.to', 'azmovies.net', 'braflix.to', 'myflixer.to', 'bflix.to',

    // --- Social Media & Forums ---
    'pinterest.com', 'snapchat.com', 'tumblr.com', 'quora.com', 'medium.com',
    'discordapp.com', 'telegram.me', 'vk.com', 'x.com', 'fandom.com', 't.me',
    'ok.ru', 'douyin.com', 'line.me', 'myspace.com', 'fb.com',

    // --- Education & Learning ---
    'coursera.org', 'edx.org', 'udemy.com', 'khanacademy.org', 'w3schools.com',
    'mozilla.org', 'freecodecamp.org', 'codecademy.com', 'instructure.com',
    'developer.mozilla.org', 'javascript.info', 'css-tricks.com', 'dev.to',
    'smashingmagazine.com', 'web.dev', 'html5rocks.com', 'scrimba.com',
    'theodinproject.com', 'github.com/education', 'studentbeans.com',
    'uni-days.com', 'obsidian.md', 'ankiweb.net', 'kahoot.com', 'quizlet.com',

    // --- Security & Privacy ---
    'lastpass.com', '1password.com', 'dashlane.com', 'nordvpn.com',
    'expressvpn.com', 'letsencrypt.org', 'surfshark.com', 'protonvpn.com',
    'cyberghostvpn.com', 'privateinternetaccess.com', 'ipvanish.com',
    'mullvad.net', 'bitwarden.com',

    // --- Domain & Hosting ---
    'godaddy.com', 'namecheap.com', 'bluehost.com', 'hostgator.com',
    'dreamhost.com', 'siteground.com', 'afternic.com', 'brandbucket.com',
    'buydomains.com', 'dan.com', 'domainmarket.com', 'expireddomains.com',
    'hugedomains.com', 'nicsell.com',

    // --- Analytics & Marketing ---
    'google-analytics.com', 'segment.com', 'mixpanel.com', 'amplitude.com',
    'hubspot.com', 'marketo.com', 'ahrefs.com',

    // --- Operating Systems & Software ---
    'ubuntu.com', 'debian.org', 'fedoraproject.org', 'centos.org', 'kubernetes.io',
    'archlinux.org', 'manjaro.org', 'linuxmint.com', 'pop.system76.com',
    'podman.io', 'vagrantup.com', 'virtualbox.org', 'homebrew.sh',
    'chocolatey.org', 'snapcraft.io', 'flatpak.org', 'brew.sh',

    // --- Mobile & Apps ---
    'play.google.com', 'apps.apple.com', 'appstore.com', 'itunes.apple.com',
    'developer.apple.com',

    // --- Research, Science & Government ---
    'nature.com', 'sciencedirect.com', 'arxiv.org', 'researchgate.net',
    'academia.edu', 'who.int', 'un.org', 'worldbank.org', 'imf.org', 'w3.org',
    'gov.uk', 'europa.eu', 'nih.gov', 'cdc.gov', 'scopus.com', 'webofscience.com',
    'pubmed.gov', 'eric.ed.gov', 'doaj.org', 'loc.gov', 'science.gov',

    // --- Regional: Amazon & Services ---
    'amazon.in', 'amazon.co.jp', 'amazon.co.uk', 'amazon.de',

    // --- Google Subdomains & Tools ---
    'music.youtube.com', 'youtu.be', 'support.google.com', 'docs.google.com',
    'policies.google.com', 'plus.google.com', 'drive.google.com',
    'accounts.google.com', 'maps.google.com', 'sites.google.com',
    'photos.google.com', 'myaccount.google.com', 'developers.google.com',
    'tools.google.com', 'news.google.com', 'get.google.com',
    'picasaweb.google.com', 'draft.blogger.com', 'bp.blogspot.com',
    'googleusercontent.com', 'googleblog.com', 'gstatic.com',
    'storage.googleapis.com', 'ytimg.com', 'goo.gl', 'forms.gle', 'share.google',
    'google.de', 'google.es', 'google.it', 'google.com.br', 'google.co.jp',
    'colab.research.google.com',

    // --- Wikipedia Regional ---
    'en.wikipedia.org', 'es.wikipedia.org', 'pt.wikipedia.org',
    'fr.wikipedia.org', 'wikimedia.org', 'wikia.com',

    // --- Microsoft Services ---
    'sharepoint.com', 'office365.com',

    // --- Content & File Sharing ---
    'blogger.com', 'wordpress.org', 'files.wordpress.com', 'mediafire.com',
    '4shared.com', 'tinyurl.com', 'archive.org', 'issuu.com', 'scribd.com',
    'dailymotion.com', 'vimeo.com', 'weebly.com', 'jimdo.com', 'opera.com',
    'istockphoto.com', 'pixabay.com', 'flickr.com', 'imgur.com', 'gravatar.com',
    'slideshare.net', 'about.me', 'linktr.ee', 'list-manage.com', 'idrive.com',
    'sync.com', 'pcloud.com', 'icedrive.com', 'mega.nz', 'box.com',

    // --- Databases & Package Managers ---
    'mongodb.com', 'postgres.org', 'mysql.com', 'redis.io', 'neo4j.com',
    'prisma.io', 'planetscale.com', 'cockroachlabs.com', 'fauna.com',
    'crates.io', 'packagist.org', 'rubygems.org', 'nuget.org', 'docker.io',
    'ghcr.io', 'devdocs.io', 'devhints.io', 'cheat.sh', 'explainshell.com',
    'tldr.sh', 'man7.org', 'linux.die.net',

    // --- Top Pakistani Sites ---
    'pakistan.gov.pk', 'pmo.gov.pk', 'sifc.gov.pk', 'ndma.gov.pk', 'molaw.gov.pk',
    'narcon.gov.pk', 'privatisation.gov.pk', 'safron.gov.pk', 'punjab.gov.pk',
    'kp.gov.pk', 'balochistan.gov.pk', 'ajk.gov.pk', 'sbp.org.pk', 'fbr.gov.pk',
    'hec.gov.pk', 'nadra.gov.pk', 'pta.gov.pk', 'secp.gov.pk', 'pmd.gov.pk',
    'pbs.gov.pk', 'na.gov.pk', 'finance.gov.pk', 'pec.org.pk', 'mofa.gov.pk',
    'pid.gov.pk', 'citizenportal.gov.pk', 'bisp.gov.pk', 'lesco.gov.pk',
    'gepco.com.pk', 'pitc.com.pk', 'aiou.edu.pk', 'vu.edu.pk', 'nust.edu.pk',
    'lums.edu.pk', 'uet.edu.pk', 'pu.edu.pk', 'comsats.edu.pk', 'muet.edu.pk',
    'riphah.edu.pk', 'mnsuam.edu.pk', 'stmu.edu.pk', 'pct.edu.pk', 'hbs.edu.pk',
    'dawn.com', 'tribune.com.pk', 'jang.com.pk', 'express.pk', 'thenews.com.pk',
    'bolnews.com', 'urdupoint.com', 'pakistantoday.com.pk', 'arynews.tv',
    'dunyanews.tv', 'geo.tv', 'aaj.tv', 'nation.com.pk', 'brecorder.com',
    'propakistani.pk', 'arabnews.pk', 'dailypakistan.com.pk', 'daraz.pk',
    'olx.com.pk', 'pakwheels.com', 'sapphireonline.pk', 'foodpanda.pk',
    'zameen.com', 'naheed.pk', 'homeshopping.pk', 'goto.com.pk', 'shopon.pk',
    'telemart.pk', 'czone.com.pk', 'shophive.com', 'limelight.pk',
    'gulahmedshop.com', 'junaidjamshed.com', 'khaadi.com', 'alkaramstudio.com',
    'bonanzasatrangi.com', 'breakout.com.pk', 'hbl.com', 'meezanbank.com',
    'bankalfalah.com', 'ubldigital.com', 'abl.com', 'mcb.com.pk',
    'faysalbank.com', 'bop.com.pk', 'bankalhabib.com', 'sc.com',
    'jazzcash.com.pk', 'easypaisa.com.pk', 'whatmobile.com.pk', 'hamariweb.com',
    'marham.pk', 'oladoc.com', 'priceoye.pk', 'healthwire.pk', 'pcb.com.pk',
    'psx.com.pk', 'bite.pk', 'njp.gov.pk', 'jobsalert.pk', 'paperpk.com',
    'galaxy.pk', 'hf-store.pk', 'intaglaptops.com', 'mega.pk', 'techbazaar.pk',
    'wajiz.pk', 'techroid.com', 'huawei.com', 'lg.com', 'panasonic.com',
    'lenovo.com', 'htc.com', 'nokia.com', 'sony.com', 'asus.com', 'dell.com',
    'hp.com', 'acer.com', 'msi.com', 'notebookcheck.net', 'nanoreview.net',
    'versus.com', 'tomshardware.com', 'gsmarena.com', 'pk.linkedin.com',

    // --- Other Jobs & Tech ---
    'indeed.com', 'cricbuzz.com', 'usps.com', 'pixiv.net', 'toasttakeout.com',
    'eat24.com', 'seamless.com', 'delivery.com', 'wolt.com', 'deliveroo.com',
    'choco.com', 'glovoapp.com', 'weworkremotely.com', 'remote.co',
    'remoteok.com', 'justremote.co', 'toptal.com', 'flexjobs.com',
    'globaljobs.org', 'edvisors.com', 'internationaljobs.com', 'careers.un.org',
    'welcometothejungle.com', 'monster.com', 'snagajob.com', 'angellist.com',
    'ziprecruiter.com',

    // =========================================================================
    // GLOBAL EDUCATION DOMAINS (Top ~200)
    // =========================================================================

    // --- Top Global Universities (US - Ivy Plus & Tech) ---
    'harvard.edu', 'mit.edu', 'stanford.edu', 'yale.edu', 'princeton.edu',
    'columbia.edu', 'caltech.edu', 'upenn.edu', 'cornell.edu', 'uchicago.edu',
    'berkeley.edu', 'ucla.edu', 'jhu.edu', 'nyu.edu', 'duke.edu',
    'northwestern.edu', 'umich.edu', 'cmu.edu', 'gatech.edu', 'utexas.edu',
    'illinois.edu', 'u.washington.edu', 'wisc.edu', 'ucsd.edu', 'ucsf.edu',
    'brown.edu', 'dartmouth.edu', 'vanderbilt.edu', 'wustl.edu', 'usc.edu',
    'rice.edu', 'nd.edu', 'georgetown.edu', 'virginia.edu', 'unc.edu',

    // --- Top Global Universities (UK & Europe) ---
    'ox.ac.uk', 'cam.ac.uk', 'imperial.ac.uk', 'ucl.ac.uk', 'ed.ac.uk',
    'manchester.ac.uk', 'kcl.ac.uk', 'lse.ac.uk', 'bristol.ac.uk', 'warwick.ac.uk',
    'ethz.ch', 'epfl.ch', 'psl.eu', 'tum.de', 'lmu.de',
    'uni-heidelberg.de', 'sorbonne-universite.fr', 'ku.dk', 'lunduniversity.lu.se', 'uva.nl',
    'tudelft.nl', 'uzh.ch', 'kuleuven.be', 'univie.ac.at', 'helsinki.fi',
    'tcd.ie', 'ucd.ie', 'gla.ac.uk', 'sheffield.ac.uk', 'birmingham.ac.uk',

    // --- Top Global Universities (Canada, Australia, NZ) ---
    'utoronto.ca', 'mcgill.ca', 'ubc.ca', 'ualberta.ca', 'uwaterloo.ca',
    'umontreal.ca', 'mcmaster.ca', 'uottawa.ca', 'ucalgary.ca', 'westernu.ca',
    'unimelb.edu.au', 'sydney.edu.au', 'unsw.edu.au', 'anu.edu.au', 'monash.edu',
    'uq.edu.au', 'uwa.edu.au', 'adelaide.edu.au', 'auckland.ac.nz', 'otago.ac.nz',

    // --- Top Global Universities (Asia & Middle East) ---
    'nus.edu.sg', 'ntu.edu.sg', 'tsinghua.edu.cn', 'pku.edu.cn', 'hku.hk',
    'ust.hk', 'cuhk.edu.hk', 'u-tokyo.ac.jp', 'kyoto-u.ac.jp', 'titech.ac.jp',
    'snu.ac.kr', 'kaist.ac.kr', 'yonsei.ac.kr', 'korea.ac.kr', 'iitb.ac.in',
    'iitd.ac.in', 'iisc.ac.in', 'um.edu.my', 'kaust.edu.sa', 'kfupm.edu.sa',
    'tau.ac.il', 'huji.ac.il', 'weizmann.ac.il', 'nycu.edu.tw', 'ntu.edu.tw',

    // --- MOOCs & Online Learning Platforms ---
    'coursera.org', 'edx.org', 'udemy.com', 'khanacademy.org', 'udacity.com',
    'futurelearn.com', 'skillshare.com', 'codecademy.com', 'pluralsight.com', 'datacamp.com',
    'masterclass.com', 'linkedin.com/learning', 'brilliant.org', 'coursehero.com', 'chegg.com',
    'quizlet.com', 'studocu.com', 'brainly.com', 'scribd.com', 'academia.edu',
    'researchgate.net', 'slideshare.net', 'superprof.com', 'preply.com', 'duolingo.com',
    'babbel.com', 'memrise.com', 'busuu.com', 'italki.com', 'lingoda.com',

    // --- Educational Tools, LMS & Infrastructure ---
    'canvas.instructure.com', 'blackboard.com', 'moodle.org', 'moodle.com', 'schoology.com',
    'google.com/classroom', 'classroom.google.com', 'kahoot.com', 'kahoot.it', 'nearpod.com',
    'padlet.com', 'edpuzzle.com', 'seesaw.me', 'classdojo.com', 'remind.com',
    'turnitin.com', 'grammarly.com', 'quillbot.com', 'zotero.org', 'mendeley.com',
    'endnote.com', 'overleaf.com', 'mathworks.com', 'wolframalpha.com', 'geogebra.org',
    'desmos.com', 'symbolab.com', 'gradescope.com', 'piazza.com', 'tophat.com',

    // --- Coding & Technical Education ---
    'freecodecamp.org', 'w3schools.com', 'geeksforgeeks.org', 'tutorialspoint.com', 'javatpoint.com',
    'hackr.io', 'realpython.com', 'scrimba.com', 'theodinproject.com', 'educative.io',
    'leetcode.com', 'hackerrank.com', 'codewars.com', 'algoexpert.io', 'frontendmentor.io',

    // --- Libraries, Reference & Open Access ---
    'jstor.org', 'sciencedirect.com', 'springer.com', 'wiley.com', 'tandfonline.com',
    'sagepub.com', 'eric.ed.gov', 'loc.gov', 'bl.uk', 'gutenberg.org',
    'archive.org', 'openstax.org', 'oercommons.org', 'merlot.org', 'doaj.org',
    'worldcat.org', 'britannica.com', 'dictionary.com', 'thesaurus.com', 'merriam-webster.com',

    // --- Student Services & Standardized Testing ---
    'collegeboard.org', 'act.org', 'ets.org', 'toefl.org', 'ielts.org',
    'gmat.com', 'mba.com', 'lsac.org', 'aamc.org', 'commonapp.org',
    'ucas.com', 'fafsa.gov', 'studentaid.gov', 'ratemyprofessors.com', 'niche.com',
    'usnews.com/education', 'timeshighereducation.com', 'topuniversities.com', 'qs.com', 'study.com',

    // =========================================================================
    // PAKISTAN EDUCATION DOMAINS (Top ~100)
    // =========================================================================

    // --- Government & Regulatory Bodies ---
    'hec.gov.pk',          // Higher Education Commission (Crucial)
    'mofept.gov.pk',       // Ministry of Federal Education
    'pec.org.pk',          // Pakistan Engineering Council
    'pmc.gov.pk',          // Pakistan Medical Commission
    'pmdc.pk',             // Pakistan Medical & Dental Council
    'ibcc.edu.pk',         // Inter Board Committee of Chairmen
    'fpsc.gov.pk',         // Federal Public Service Commission
    'ppsc.gop.pk',         // Punjab Public Service Commission
    'spsc.gos.pk',         // Sindh Public Service Commission
    'kppsc.gov.pk',        // KP Public Service Commission
    'bpsc.gob.pk',         // Balochistan Public Service Commission

    // --- Testing Services (High Phishing Risk) ---
    'nts.org.pk',          // National Testing Service
    'pts.org.pk',          // Pakistan Testing Service
    'ots.org.pk',          // Open Testing Service
    'cts.org.pk',          // Candidates Testing Services
    'eta.edu.pk',          // Educational Testing Council (ETC)

    // --- Federal & Capital (Islamabad) Universities ---
    'nust.edu.pk',         // NUST (Top Engineering)
    'qau.edu.pk',          // Quaid-i-Azam University
    'comsats.edu.pk',      // COMSATS (All campuses)
    'pieas.edu.pk',        // PIEAS (Nuclear/Engineering)
    'aiou.edu.pk',         // Allama Iqbal Open Univ (Huge traffic)
    'iiu.edu.pk',          // International Islamic University
    'bahria.edu.pk',       // Bahria University
    'au.edu.pk',           // Air University
    'numl.edu.pk',         // NUML (Languages)
    'ist.edu.pk',          // Inst of Space Technology
    'pide.org.pk',         // PIDE
    'cust.edu.pk',         // Capital Univ of Science & Tech
    'riphah.edu.pk',       // Riphah International
    'szabist-isb.edu.pk',  // SZABIST Islamabad
    'fast.nu.edu.pk',      // FAST NUCES (Main Domain)
    'nu.edu.pk',           // FAST NUCES (Alt)

    // --- Punjab Universities ---
    'pu.edu.pk',           // Punjab University (Lahore)
    'lums.edu.pk',         // LUMS
    'uet.edu.pk',          // UET Lahore
    'uaf.edu.pk',          // Univ of Agriculture Faisalabad
    'bzu.edu.pk',          // Bahauddin Zakariya (Multan)
    'iub.edu.pk',          // Islamia Univ Bahawalpur
    'gcu.edu.pk',          // GCU Lahore
    'gcuf.edu.pk',         // GCU Faisalabad
    'uol.edu.pk',          // University of Lahore
    'umt.edu.pk',          // UMT Lahore
    'ucp.edu.pk',          // UCP Lahore
    'uos.edu.pk',          // Univ of Sargodha
    'uog.edu.pk',          // Univ of Gujrat
    'vu.edu.pk',           // Virtual University (Huge online traffic)
    'uhs.edu.pk',          // Univ of Health Sciences
    'kemu.edu.pk',         // King Edward Medical Univ
    'fjmu.edu.pk',         // Fatima Jinnah Medical
    'uvas.edu.pk',         // Veterinary & Animal Sciences
    'superior.edu.pk',     // Superior University
    'hitecuni.edu.pk',     // HITEC Taxila
    'uettaxila.edu.pk',    // UET Taxila
    'nca.edu.pk',          // National College of Arts

    // --- Sindh Universities ---
    'uok.edu.pk',          // Karachi University
    'neduet.edu.pk',       // NED UET
    'iba.edu.pk',          // IBA Karachi
    'aku.edu',             // Aga Khan University (Global domain)
    'duhs.edu.pk',         // Dow Univ of Health Sciences
    'muet.edu.pk',         // Mehran UET (Jamshoro)
    'usindh.edu.pk',       // University of Sindh
    'jsmu.edu.pk',         // Jinnah Sindh Medical Univ
    'szabist.edu.pk',      // SZABIST (Main)
    'iobm.edu.pk',         // IoBM (CBM)
    'smiu.edu.pk',         // Sindh Madressatul Islam
    'lumhs.edu.pk',        // Liaquat Univ of Medical Health
    'iba-suk.edu.pk',      // Sukkur IBA
    'quest.edu.pk',        // Quaid-e-Awam (Nawabshah)
    'salu.edu.pk',         // Shah Abdul Latif Univ
    'jinnah.edu',          // MAJU
    'icmap.com.pk',        // ICMAP (Cost & Mgmt Accountants)

    // --- Khyber Pakhtunkhwa (KPK) Universities ---
    'uop.edu.pk',          // University of Peshawar
    'uetpeshawar.edu.pk',  // UET Peshawar
    'giki.edu.pk',         // GIKI (Top Engineering)
    'kmu.edu.pk',          // Khyber Medical University
    'awkum.edu.pk',        // Abdul Wali Khan Univ
    'aup.edu.pk',          // Agriculture Univ Peshawar
    'kust.edu.pk',         // Kohat Univ
    'uswat.edu.pk',        // Univ of Swat
    'hu.edu.pk',           // Hazara University
    'imsciences.edu.pk',   // IMSciences Peshawar

    // --- Balochistan & AJK Universities ---
    'uob.edu.pk',          // Univ of Balochistan
    'buitms.edu.pk',       // BUITEMS (Quetta)
    'ajku.edu.pk',         // Univ of Azad Jammu Kashmir
    'must.edu.pk',         // Mirpur Univ of Sci & Tech

    // --- Major Educational Boards (BISE) - High Student Traffic ---
    'fbise.edu.pk',        // Federal Board
    'biselahore.com',      // BISE Lahore
    'biserawalpindi.edu.pk', // BISE Rawalpindi
    'bisegrw.edu.pk',      // BISE Gujranwala
    'bisemultan.edu.pk',   // BISE Multan
    'bisefaisalabad.edu.pk', // BISE Faisalabad
    'bisesargodha.edu.pk', // BISE Sargodha
    'bisesahiwal.edu.pk',  // BISE Sahiwal
    'bisedgkhan.edu.pk',   // BISE DG Khan
    'bisebwp.edu.pk',      // BISE Bahawalpur
    'biek.edu.pk',         // Board of Intermediate Karachi
    'bsek.edu.pk',         // Board of Secondary Karachi
    'bisehyd.edu.pk',      // BISE Hyderabad
    'bisesuksindh.edu.pk', // BISE Sukkur
    'bisep.edu.pk',        // BISE Peshawar
    'biseabbottabad.edu.pk', // BISE Abbottabad
    'bisemardan.edu.pk',   // BISE Mardan
    'biseswat.edu.pk',     // BISE Swat
    'ajkbise.net'          // AJK Board
]);