export type LynchClassification =
  | 'stalwart'
  | 'cyclical'
  | 'turnaround'
  | 'fast_grower'
  | 'slow_grower'
  | 'asset_play'

export type LynchNarrative = {
  classification: LynchClassification
  companyDescription: string
  lynchClassStory: string
  selfVerification: readonly [string, string, string]
  newsFilter: string
}

export const LYNCH_NARRATIVES = {
  BAJFINANCE: {
    classification: 'fast_grower',
    companyDescription:
      'Bajaj Finance is a financial services company. It lends money to people and businesses across India. A customer may use its finance for a phone, a home appliance, a vehicle, a small firm, or a personal need. It also offers deposits and payment tools. This means the company earns mainly from interest and fees. Its work depends on finding suitable borrowers, checking their ability to repay, and collecting payments on time. Technology helps it serve many customers and make quick decisions. The basic idea is simple, but lending is never risk-free. If jobs, incomes, or small businesses weaken, more borrowers may miss payments. The company must also borrow money before it can lend money. Changes in funding cost can therefore affect its results. Bajaj Finance sits in the Financial Services sector, so credit quality, funding access, and careful growth matter as much as customer demand.',
    lynchClassStory:
      'The instruments table places Bajaj Finance in the fast grower class. That label describes the growth story, not a promise about future returns. The company has expanded by reaching more customers, offering more kinds of loans, and using data to serve them at scale. A fast grower can build a larger business quickly when demand, funding, and repayment quality work together. The hard part is keeping all three in balance. Rapid lending can look strong at first while creating later problems if checks become loose. For this company, the useful questions are whether customer growth is still healthy, overdue loans remain controlled, and funding stays available at a fair cost. It is also worth watching whether new products add lasting relationships or only short bursts of activity. This story differs from a steady bank or a commodity producer: its main test is whether a high pace of expansion remains disciplined.',
    selfVerification: [
      'Can you explain, in your own words, how Bajaj Finance earns interest and fees from lending?',
      'Would you be comfortable staying patient through a 20% price drop while checking missed payments and funding costs?',
      'Does the fast grower story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about loan growth, missed payments, funding costs, regulation, major products, or leadership that can change this story. Leave out price chatter, repeated summaries, rumours without a named source, and general market noise. A headline must never make a stronger claim than its source.',
  },
  COALINDIA: {
    classification: 'slow_grower',
    companyDescription:
      'Coal India is a large coal mining company owned mainly by the Government of India. Its mines supply fuel used by power plants and some industrial customers. The company finds coal deposits, removes earth, mines the coal, moves it by road or rail, and supplies customers under set arrangements or auctions. India still uses coal for much of its electricity, so the company supports a basic part of the energy system. Yet this is not a simple growth market. Mine approvals, land, rail links, worker safety, weather, and environmental rules can all affect output. Prices may also differ across customer groups. Coal India sits in the Mining sector. Its cash generation often depends on production volume, customer demand, wage costs, and rules set by the state. Over a longer period, cleaner energy may change coal use, but the speed of that change depends on power demand and grid needs.',
    lynchClassStory:
      'The instruments table places Coal India in the slow grower class. A slow grower often serves a mature need and expands at a measured pace. Coal India is not mainly trying to invent a new market. Its task is to supply a long-used fuel reliably while handling large mines and public duties. Growth may come from higher output, better transport, or improved mine work, but physical and policy limits make sudden expansion hard. The story can still produce strong cash in some years, especially when volumes and prices are supportive. That does not turn it into a fast grower. The key checks are whether output plans are met, customers can take delivery, costs stay controlled, and energy policy changes the role of coal. Payments to shareholders can use cash, but they do not by themselves prove that the core business is growing. This class fits a mature operator whose future is tied to steady execution and a slowly changing energy mix.',
    selfVerification: [
      'Can you explain how mined coal reaches power and industrial customers, and where Coal India earns its money?',
      'Would you be comfortable staying patient through a 20% price drop while checking output, costs, policy, and power demand?',
      'Does the slow grower story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about mine output, dispatches, auctions, wages, rail capacity, safety, environmental rules, or power demand. Leave out daily price chatter, political remarks with no operating effect, repeated stories, and rumours without a named source. A headline must never make a stronger claim than its source.',
  },
  DLF: {
    classification: 'asset_play',
    companyDescription:
      'DLF is a real estate company. It develops homes, offices, shops, and other large properties, mainly in major Indian cities. Part of the business builds and transfers homes to customers. Another part owns completed commercial space and earns rent from companies and retailers. This mix matters because development income can arrive in uneven stages, while rent can be more regular. Land is a key raw material. A site may take years to gain approvals, receive roads and services, launch, and turn into cash. Customer confidence, home-loan rates, office demand, construction cost, and local rules all shape the outcome. DLF sits in the Real Estate sector. A simple sales number never tells the whole story. One must also understand bookings, construction progress, customer collections, debt, rental use, and the quality and location of land that may support future projects.',
    lynchClassStory:
      'The instruments table places DLF in the asset play class. This class is used when valuable assets may be central to understanding the business. For DLF, those assets include land, planned projects, and income-producing commercial property. Their worth cannot be read from one quarter alone. A well-located land parcel may create value only after approvals and development. An office building may look valuable, but empty space or weak rents can reduce the cash it makes. The story therefore rests on what the assets are, where they are, what claims sit against them, and how well management turns them into cash. Rising property prices can help, but they can also invite overconfidence. Debt and long project timelines can make errors costly. This is different from a fast grower driven mainly by unit sales. DLF’s case asks whether the market and the accounts fully reflect a complex property base and whether that base is being developed with care.',
    selfVerification: [
      'Can you explain the difference between DLF building homes for customers and earning rent from completed property?',
      'Would you be comfortable staying patient through a 20% price drop while checking debt, bookings, rent, and project approvals?',
      'Does the asset play story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about launches, bookings, collections, debt, rental use, land, approvals, or major legal matters tied to property. Leave out broker targets, daily price chatter, repeated launch publicity, and rumours without documents or named sources. A headline must never make a stronger claim than its source.',
  },
  HDFCBANK: {
    classification: 'stalwart',
    companyDescription:
      'HDFC Bank is a large private bank serving people and businesses across India. It accepts deposits, provides payment services, and lends for homes, vehicles, personal needs, working capital, and larger business plans. The bank earns much of its money from the gap between interest received on loans and interest paid on deposits. It also earns fees from services. A bank can grow only if people trust it with money and if its loans are repaid. That makes low-cost deposits, careful lending, and strong systems important. HDFC Bank sits in the Financial Services sector. Its size gives it a wide customer base and many branches and digital links, but size does not remove risk. Credit losses, fraud, regulation, technology failures, and a poor mix of loans or deposits can hurt. After a major merger, joining systems, customers, and funding needs also requires patient work.',
    lynchClassStory:
      'The instruments table places HDFC Bank in the stalwart class. A stalwart is a large, established company with a proven place in its market. It may still grow, but its story is usually about durable service and sound execution rather than a tiny base becoming huge. HDFC Bank fits because it handles a broad range of everyday banking needs for millions of customers. Its large network and long record can support trust, deposits, and repeat use. The class is not a safety stamp. A large bank can still make weak loans or pay too much for funding. The useful test is whether the bank keeps deposit growth, loan growth, and credit quality in balance as it becomes larger. One should also watch whether merger-related changes settle without harming service or costs. This is a steadier story than a specialist lender racing into new products: strength comes from a wide base, discipline, and the ability to manage scale.',
    selfVerification: [
      'Can you explain how HDFC Bank uses deposits to support loans and earns from the interest gap and fees?',
      'Would you be comfortable staying patient through a 20% price drop while checking deposits, loan quality, and merger progress?',
      'Does the stalwart story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about deposits, loan growth, missed payments, margins, regulation, technology, or merger execution. Leave out daily price chatter, routine branch publicity, repeated summaries, and rumours without a named source. A headline must never make a stronger claim than its source.',
  },
  HINDALCO: {
    classification: 'cyclical',
    companyDescription:
      'Hindalco Industries makes aluminium and copper products. Its work starts with raw materials and energy, then moves through refining, smelting, rolling, and shaping metal for customers. These metals are used in vehicles, buildings, electrical systems, packaging, and many other goods. Through its wider operations, the company also makes flat aluminium products used by customers in different countries. Hindalco sits in the Metals sector. The business can gain when factories and construction need more metal, but it can face pressure when demand weakens or too much supply reaches the market. Metal prices are only one part of the picture. Coal, power, freight, currency moves, mine supply, plant use, and the mix of basic versus shaped products also matter. Large plants cost a great deal and cannot be turned on and off without care, so weak market periods can test cash and debt.',
    lynchClassStory:
      'The instruments table places Hindalco in the cyclical class. A cyclical company moves with an economic and industry cycle. When demand is firm and metal supply is tight, prices and plant use may support results. When construction, manufacturing, or vehicle demand slows, the same plants can earn much less. Hindalco is not just a simple bet on one metal price because it has several products and regions. More processed products may soften part of the swing, but they do not remove the cycle. The right story question is not only whether aluminium or copper is rising today. It is whether current prices are near a strong or weak part of the cycle, how costs are moving, and whether debt and projects can be managed if conditions turn. Treating one unusually good year as normal would miss the class. A cyclical reading asks the learner to expect changing margins and to study supply, demand, and cost together.',
    selfVerification: [
      'Can you explain how Hindalco turns raw materials into aluminium and copper products used by other industries?',
      'Would you be comfortable staying patient through a 20% price drop while checking metal demand, energy cost, debt, and supply?',
      'Does the cyclical story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about metal demand, global supply, energy and raw-material costs, plant use, debt, projects, or trade rules. Leave out daily metal-price recaps with no company link, repeated stories, and rumours without a named source. A headline must never make a stronger claim than its source.',
  },
  INFY: {
    classification: 'fast_grower',
    companyDescription:
      'Infosys is an information technology services company. It helps large organisations build and run software, move work to cloud systems, use data, improve business tasks, and protect digital operations. Most customers are outside India, so the company earns much of its revenue in foreign currencies while many employees and costs are in India. Its main assets are people, skills, customer ties, delivery methods, and trust rather than factories. Infosys sits in the Information Technology sector. A project can last for years, but customers may delay new work when their own outlook is weak. The company must keep learning as technology changes. It must also hire, train, and retain people without letting staff costs rise faster than revenue. Contract wins sound useful, yet the timing and profit from those contracts matter. Currency changes can lift or lower reported results even when the work itself is steady.',
    lynchClassStory:
      'The instruments table places Infosys in the fast grower class. The label reflects a business built to expand through new technology work, more services for existing customers, and entry into new areas. Unlike a factory, a services company can add skilled teams and repeat its delivery model across many clients. That can support growth when companies spend more on digital change. The fast grower story still needs proof. Large size makes each extra step harder, and new tools may change the kind of work customers need. A long list of contracts is not enough if revenue starts slowly or prices are weak. The useful checks are growth in real client work, the share of large deals that becomes revenue, staff use, profit per project, and customer spending plans. This story is different from a stalwart bank or cyclical metal maker: the central question is whether Infosys can keep turning skill and trust into new, profitable work at a healthy pace.',
    selfVerification: [
      'Can you explain what technology work Infosys performs for large organisations and why those customers keep using it?',
      'Would you be comfortable staying patient through a 20% price drop while checking client spending, staff use, and project profit?',
      'Does the fast grower story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about client budgets, large contracts, project starts, staff use, pricing, leadership, currency, or major technology shifts. Leave out vague trend pieces, routine award notices, daily price chatter, and rumours without a named source. A headline must never make a stronger claim than its source.',
  },
  ITC: {
    classification: 'slow_grower',
    companyDescription:
      'ITC is a consumer goods company with several businesses. Cigarettes have long provided a large share of its profit. It also makes packaged foods, personal-care goods, notebooks, and other everyday products. The company works with farmers through its agri business and makes paperboards and packaging. These parts have different customers, costs, and risks. A strong distribution network helps products reach shops across India. Brands and repeat use matter because many items are low-cost choices made often. ITC sits in the Consumer Staples sector. Tobacco taxes and rules can change demand and legal conditions. Food and personal-care brands face strong rivals and need spending on factories, advertising, and shelf space. Farm and paper operations can move with crop supply, input costs, and industrial demand. The business is therefore broad, but its parts should not be treated as if they grow or earn in the same way.',
    lynchClassStory:
      'The instruments table places ITC in the slow grower class. Much of the company rests on mature products with wide reach, especially cigarettes. Such a base can create regular cash, but it is unlikely to multiply simply because the market is new. Growth may come from price changes, wider use of packaged goods, better product mix, and patient building of newer brands. Those efforts can take years and may earn less than the older core while they scale. The slow grower label keeps the story grounded: steady cash and broad distribution matter, but neither guarantees quick expansion. The useful checks are tobacco volume and tax rules, profit from newer consumer goods, raw-material costs, and how cash is used across the group. This differs from a fast grower whose main question is how long high expansion can last. For ITC, the question is whether a mature cash engine and younger brands can improve together without waste.',
    selfVerification: [
      'Can you explain which ITC businesses make everyday products and why cigarettes still matter to the whole company?',
      'Would you be comfortable staying patient through a 20% price drop while checking taxes, brand progress, costs, and cash use?',
      'Does the slow grower story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about tobacco rules, tax, product volumes, consumer-brand profit, farm inputs, paper costs, or major changes in the group. Leave out product-launch publicity with no business effect, repeated stories, daily price chatter, and unnamed rumours. A headline must never make a stronger claim than its source.',
  },
  LT: {
    classification: 'stalwart',
    companyDescription:
      'Larsen & Toubro is a large engineering and construction company. It designs and builds complex projects such as transport links, power systems, factories, water works, and defence equipment. It also has technology and financial interests, but large projects are central to its identity. Customers include governments and major businesses in India and abroad. L&T sits in the Construction sector. An order may look impressive, yet the company earns over time as work is completed. It must estimate labour, steel, cement, equipment, time, and site risks before agreeing on a price. Delays or poor estimates can reduce profit. Cash collection matters because the company may spend on work before a customer pays. The order book gives a view of future activity, but order quality, contract terms, and execution are as important as the total number. Safety and engineering skill are also basic parts of the business.',
    lynchClassStory:
      'The instruments table places L&T in the stalwart class. It is an established operator with a long record in projects that smaller firms may struggle to plan, fund, or execute. Its scale, skills, and customer ties can help it compete for major work. A stalwart story is less about discovering a brand-new market and more about carrying a large, proven system forward. India’s infrastructure needs can provide years of work, but the label is not a guarantee of smooth results. Projects are uneven, working capital can rise, and a large order can become a problem if costs or timelines were judged poorly. The useful checks are fresh orders, the mix and quality of the order book, project margins, cash collection, and debt. This is different from an asset play based on hidden land or a cyclical metal producer. L&T’s story depends on dependable execution at scale and on turning engineering work into cash.',
    selfVerification: [
      'Can you explain how L&T wins a large project, completes it over time, and turns that work into revenue and cash?',
      'Would you be comfortable staying patient through a 20% price drop while checking order quality, margins, delays, and collections?',
      'Does the stalwart story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about major orders, cancellations, project progress, cost changes, margins, cash collection, safety, or government spending tied to its work. Leave out small award notices, repeated order headlines, daily price chatter, and unnamed rumours. A headline must never make a stronger claim than its source.',
  },
  PIDILITIND: {
    classification: 'fast_grower',
    companyDescription:
      'Pidilite Industries makes adhesives, sealants, construction chemicals, and art materials. Its products help join wood, fix tiles, stop leaks, repair homes, and support craft work. Well-known brands, shop reach, and ties with carpenters, plumbers, painters, and builders are important parts of the business. Many purchases are small, but they happen across a very large number of homes and work sites. Pidilite sits in the Chemicals sector. The company earns when people build, repair, decorate, and improve property. Raw materials linked to chemicals and crude oil can change costs. Passing those changes to customers may take time. Brand trust matters because a failed adhesive or water treatment can cost far more than the product itself. Growth also depends on keeping products easy to find, teaching users how to apply them, and adding useful products without making the range confusing or weak.',
    lynchClassStory:
      'The instruments table places Pidilite Industries in the fast grower class. Its path is based on selling more trusted products to more users and widening from adhesives into nearby repair and construction needs. A strong brand can help a small item become the default choice for tradespeople and families. Distribution and user habits can then support repeat demand. The fast grower label asks whether that engine is still expanding, not whether past brand success will repeat by itself. Housing activity, home repair, new categories, and overseas operations may add growth. Raw-material inflation, weak construction, or poor new products may slow it. The useful checks are volume growth, market reach, profit after input costs, and whether newer products earn loyal use. This is not a commodity chemical story where one market price rules the result. Pidilite must keep turning trust, teaching, and distribution into profitable demand at a pace above a mature consumer business.',
    selfVerification: [
      'Can you explain why users choose Pidilite products and how brands and trade links support repeat demand?',
      'Would you be comfortable staying patient through a 20% price drop while checking volumes, raw-material costs, and new categories?',
      'Does the fast grower story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about product volumes, housing and repair demand, raw-material costs, pricing, distribution, acquisitions, or major product problems. Leave out minor campaign news, daily price chatter, repeated summaries, and rumours without a named source. A headline must never make a stronger claim than its source.',
  },
  RELIANCE: {
    classification: 'stalwart',
    companyDescription:
      'Reliance Industries is a large group with several major businesses. It processes crude oil, makes fuels and chemicals, runs the Jio mobile and digital network, and operates a wide retail network. These parts serve very different customers. Energy products can move with global prices and refining conditions. Telecom depends on subscribers, network use, service prices, and heavy investment. Retail depends on store and online sales, product mix, and customer demand. Reliance sits in the Diversified sector because no single simple activity describes the whole group. Its size can provide cash, reach, and the ability to fund new projects, but it also makes the accounts harder to read. A learner should separate each main business, understand which one produces cash, and see where that cash is being invested. Debt, large projects, regulation, and deals between group parts also deserve attention.',
    lynchClassStory:
      'The instruments table places Reliance Industries in the stalwart class. It is a large, established company with important positions in energy, telecom, and retail. Its story is not that a small company needs only one idea to become large. It is about whether a powerful group can run mature cash-producing operations while building newer engines with discipline. Scale may lower some costs and widen customer reach, but it can also hide weak parts behind strong ones. The stalwart label therefore calls for patient checks: refining and chemical conditions, Jio customer value, retail profit, project spending, debt, and clear reporting across the group. One division may be rising while another is falling. A single group growth number can miss that. This differs from a pure cyclical producer or a focused fast grower. Reliance’s main test is whether its many large businesses support one another and whether new investment creates lasting cash rather than complexity alone.',
    selfVerification: [
      'Can you explain how Reliance makes money from energy, Jio, and retail without treating them as one business?',
      'Would you be comfortable staying patient through a 20% price drop while checking each division, debt, and project spending?',
      'Does the stalwart story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about refining, chemicals, Jio, retail, major projects, debt, regulation, or group transactions with a clear business effect. Leave out daily price chatter, repeated deal rumours, and broad market stories. A headline must never make a stronger claim than its source.',
  },
  TATASTEEL: {
    classification: 'cyclical',
    companyDescription:
      'Tata Steel makes steel used in buildings, vehicles, machines, railways, and consumer goods. The process uses iron ore, coal, energy, large plants, and skilled workers. The company has operations in India and Europe, so demand, costs, and rules can differ across regions. Some raw materials come from its own mines, which can help in certain markets, but steel prices still depend on wider supply and demand. Tata Steel sits in the Metals sector. Steel plants carry high fixed costs and need good use to work well. When construction and manufacturing are busy, orders and prices may improve. When demand slows or imports rise, profit can fall quickly. Energy costs, freight, environmental rules, plant upgrades, debt, and labour matters also shape results. A tonne of steel sold is not enough information; the product type, market, cost, and region all affect what the company earns.',
    lynchClassStory:
      'The instruments table places Tata Steel in the cyclical class. Steel demand rises and falls with construction, vehicles, machines, and the wider economy. Supply also changes as mills open, close, or export into new markets. That creates periods of strong and weak prices. Tata Steel’s results can therefore look best near a high point in the cycle and worst near a low point. This makes simple recent-profit comparisons risky. The learner should ask what part of the cycle current earnings reflect. Indian mines and operations may behave differently from European plants, where energy, demand, and change costs can be harder. The useful checks are steel prices, plant use, raw-material and energy costs, imports, regional performance, debt, and spending on cleaner production. This story is not about smooth yearly progress. It expects swings and asks whether the company can remain sound through weak periods while using strong periods wisely.',
    selfVerification: [
      'Can you explain how Tata Steel turns raw materials into products and why construction and factory demand affect it?',
      'Would you be comfortable staying patient through a 20% price drop while checking the steel cycle, costs, debt, and regions?',
      'Does the cyclical story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about steel demand, imports, prices, plant use, mines, energy costs, European operations, debt, or major projects. Leave out daily metal-price recaps with no company effect, repeated summaries, and unnamed rumours. A headline must never make a stronger claim than its source.',
  },
  TCS: {
    classification: 'stalwart',
    companyDescription:
      'Tata Consultancy Services is a large information technology services company. It helps banks, retailers, manufacturers, governments, and other organisations build and run software and digital systems. Work includes cloud services, data, security, consulting, and support for important daily operations. Many customer ties last for years because changing a core system can be costly and risky. TCS earns much of its revenue outside India, while a large share of its staff works from India and other delivery centres. It sits in the Information Technology sector. The business needs skilled people, strong delivery, and customer trust more than heavy factories. Client budgets, contract prices, staff costs, currency changes, and the move toward new tools can all affect results. Large contract announcements need context: the work may start in stages, and revenue and profit depend on the exact terms and how well teams deliver.',
    lynchClassStory:
      'The instruments table places TCS in the stalwart class. TCS has large scale, a long operating record, and deep ties with major customers. Much of its strength comes from being trusted to run systems that clients cannot easily stop. That creates repeat work, but it does not make growth automatic. A very large company needs a great deal of new revenue to grow quickly, and changing technology can alter the work clients need. The stalwart story is therefore about keeping customer trust, renewing and expanding work, training people, and protecting project profit. The useful checks are client spending, large-deal conversion, staff use, pricing, customer concentration, and how new technology changes services. This differs from a smaller fast grower chasing a new market. TCS’s test is whether an established service machine can adapt without losing quality or discipline. Stability comes from relationships and execution, not from the class name alone.',
    selfVerification: [
      'Can you explain why large organisations trust TCS with important systems and how long projects create revenue?',
      'Would you be comfortable staying patient through a 20% price drop while checking client budgets, staff use, and project profit?',
      'Does the stalwart story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about client budgets, major contracts, project starts, pricing, staff use, leadership, currency, or technology that changes service demand. Leave out routine awards, vague trend stories, daily price chatter, and unnamed rumours. A headline must never make a stronger claim than its source.',
  },
  TITAN: {
    classification: 'fast_grower',
    companyDescription:
      'Titan Company makes and retails jewellery, watches, eyewear, and other lifestyle products. Jewellery is the largest part of the business. Customers care about design, purity, trust, service, and the ability to exchange or repair products. Stores and brands help Titan turn those needs into repeat visits. Watches and eyewear use some of the same skills in design, branding, and retail, though each market works differently. Titan sits in the Consumer Discretionary sector because many purchases can be delayed when household confidence is weak. Gold prices can change the amount customers purchase and the cash needed to stock jewellery. Store growth, sales from each store, product mix, making charges, competition, and inventory control all matter. Festival and wedding seasons can move demand between quarters, so one short period may not show the full trend. Trust is especially important when the item is valuable.',
    lynchClassStory:
      'The instruments table places Titan in the fast grower class. The company has expanded by bringing more jewellery purchases into organised branded stores, opening locations, and serving more types of customers. A trusted name can gain share even when the wider jewellery market grows more slowly. Watches, eyewear, and newer lifestyle lines add other paths, but jewellery still carries much of the story. A fast grower must prove that expansion is useful, not just rapid. New stores should attract enough demand, inventory should move, and growth should not rely only on higher gold prices. The useful checks are customer growth, sales volumes, store productivity, market share, margins, and cash tied up in stock. This differs from a mature slow grower whose network is mostly built. Titan’s question is how long brand trust and organised retail can keep widening the business while it controls the special risks of valuable inventory and changing consumer demand.',
    selfVerification: [
      'Can you explain why trust, stores, design, and inventory matter to Titan’s jewellery and lifestyle businesses?',
      'Would you be comfortable staying patient through a 20% price drop while checking volumes, store use, margins, and gold effects?',
      'Does the fast grower story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about customer demand, store growth, jewellery volumes, gold effects, margins, inventory, regulation, or major brand issues. Leave out festival publicity, minor launches, daily price chatter, repeated summaries, and unnamed rumours. A headline must never make a stronger claim than its source.',
  },
  TMCV: {
    classification: 'cyclical',
    companyDescription:
      'Tata Motors Commercial Vehicles makes trucks, buses, vans, and other vehicles used to move goods and people. Customers include transport firms, small operators, businesses, and public bodies. Demand depends on freight activity, road building, replacement of old fleets, financing, fuel costs, and business confidence. A vehicle maker also depends on steel, electronics, engines, suppliers, dealers, service centres, and careful factory use. TMCV sits in the Automobiles sector. Commercial vehicles are working assets for customers, so the earning ability of a truck or bus matters as much as its purchase price. Service reach and spare parts can shape the choice. The company began as a separate listed business after a demerger, so its own record must be built from that clean starting point. Planned integration work and large business changes may add opportunity, cost, and execution risk.',
    lynchClassStory:
      'The instruments table places TMCV in the cyclical class. Commercial vehicle demand often rises when freight, construction, mining, and public transport spending are active. It can fall when business slows, loans become costly, fleets have spare capacity, or operators delay replacement. Factories and dealer networks carry costs through both parts of that cycle, so profit can move faster than unit sales. The new standalone company also has limited separate history, which makes old group results an imperfect guide. The useful checks are industry volumes, market share, factory use, discounts, input costs, customer finance, service quality, and cash through a weak demand period. Integration plans need their own evidence rather than automatic credit. This is not a smooth consumer-brand story. The cyclical label tells the learner to expect strong and weak stretches, separate business skill from a friendly market, and judge whether the company stays disciplined across the full vehicle cycle.',
    selfVerification: [
      'Can you explain who uses TMCV vehicles and why freight, construction, fleet age, and finance affect demand?',
      'Would you be comfortable staying patient through a 20% price drop while checking the vehicle cycle and standalone execution?',
      'Does the cyclical story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about vehicle volumes, market share, freight, fleet replacement, financing, factory use, input costs, service, or integration progress. Leave out monthly data with no context, daily price chatter, repeated summaries, and unnamed rumours. A headline must never make a stronger claim than its source.',
  },
  TMPV: {
    classification: 'turnaround',
    companyDescription:
      'Tata Motors Passenger Vehicles makes cars and sport utility vehicles for personal use. Its range includes petrol, diesel, and electric models. Customers judge design, safety, price, features, running cost, service, and resale value. The company depends on factories, suppliers, dealers, finance partners, software, batteries, and a wide repair network. TMPV sits in the Automobiles sector. Car demand can change with household confidence, loan rates, fuel prices, new model cycles, and competition. Electric vehicles add a second race involving battery cost, charging, range, and changing policy. The company began as a separate listed business after a demerger, so it needs to establish its own public record. Past results from a combined group cannot simply be copied across. Market share, discounts, factory use, warranty cost, new-model reception, and cash needs help show whether the standalone business is becoming stronger.',
    lynchClassStory:
      'The instruments table places TMPV in the turnaround class. A turnaround story begins with a business that must show clear improvement, not merely take part in a growing market. For TMPV, the proof must come from competitive models, stable market share, better factory use, controlled discounts, product quality, and sound cash use as a standalone company. Electric vehicles may support the story, but early leadership can narrow when rivals launch more choices. A new model can lift attention for a while; lasting progress needs repeat customer demand and good service after the vehicle leaves the showroom. The limited post-demerger record makes patience and evidence especially important. The useful question is what has actually changed in operations and whether that change can last. This differs from a stalwart with a long separate record or a cyclical truck maker mainly tied to freight. TMPV must earn confidence through visible repair and stronger execution over several periods.',
    selfVerification: [
      'Can you explain how TMPV competes for car customers and why models, dealers, quality, and factory use matter?',
      'Would you be comfortable staying patient through a 20% price drop while checking whether the operating repair remains on track?',
      'Does the turnaround story match what you already believed about this company, and what evidence could change your view?',
    ],
    newsFilter:
      'Future news rule: show no more than three items, ranked by relevance. Include only reports about model demand, market share, discounts, factory use, quality, electric vehicles, dealer service, cash needs, or standalone progress. Leave out launch excitement without sales evidence, daily price chatter, repeated summaries, and unnamed rumours. A headline must never make a stronger claim than its source.',
  },
} as const satisfies Record<string, LynchNarrative>

export type LynchNarrativeTicker = keyof typeof LYNCH_NARRATIVES

export function getLynchNarrative(ticker: string): LynchNarrative | undefined {
  return LYNCH_NARRATIVES[ticker.toUpperCase() as LynchNarrativeTicker]
}
